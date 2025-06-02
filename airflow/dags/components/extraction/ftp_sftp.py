import os
import pandas as pd
from typing import Dict
from airflow.decorators import task
import paramiko
import ftplib
import tempfile

UPLOAD_DIR = "/shared_data/"

@task
def ftp_sftp(host: str, username: str, password: str, remote_path: str, 
             protocol: str = "SFTP", port: int = 22) -> Dict[str, str]:
    """
    Download files from FTP/SFTP server.
    
    Args:
        host: FTP/SFTP server host
        username: Username for authentication
        password: Password for authentication
        remote_path: Remote file or directory path
        protocol: Transfer protocol (FTP or SFTP)
        port: Server port (22 for SFTP, 21 for FTP)
    
    Returns:
        Dictionary containing downloaded file data and metadata
    """
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        if protocol.upper() == "SFTP":
            return _handle_sftp(host, username, password, remote_path, port)
        elif protocol.upper() == "FTP":
            return _handle_ftp(host, username, password, remote_path, port)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
            
    except Exception as e:
        raise ValueError(f"FTP/SFTP operation failed: {e}")

def _handle_sftp(host: str, username: str, password: str, remote_path: str, port: int) -> Dict[str, str]:
    """Handle SFTP file transfer"""
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to SFTP server
        ssh_client.connect(
            hostname=host,
            username=username,
            password=password,
            port=port,
            timeout=30
        )
        
        sftp = ssh_client.open_sftp()
        
        # Check if remote_path is a file or directory
        try:
            file_stat = sftp.stat(remote_path)
            is_file = not hasattr(file_stat, 'st_mode') or not (file_stat.st_mode & 0o040000)
        except:
            # Assume it's a file if stat fails
            is_file = True
        
        downloaded_files = []
        
        if is_file:
            # Download single file
            filename = os.path.basename(remote_path)
            local_path = os.path.join(UPLOAD_DIR, filename)
            sftp.get(remote_path, local_path)
            downloaded_files.append((filename, local_path))
        else:
            # Download all files from directory
            files = sftp.listdir(remote_path)
            for filename in files:
                remote_file = os.path.join(remote_path, filename).replace('\\', '/')
                local_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    sftp.get(remote_file, local_path)
                    downloaded_files.append((filename, local_path))
                except Exception as e:
                    print(f"Warning: Failed to download {filename}: {e}")
        
        sftp.close()
        
        # Process downloaded files
        return _process_downloaded_files(downloaded_files, "SFTP", host, remote_path)
        
    finally:
        ssh_client.close()

def _handle_ftp(host: str, username: str, password: str, remote_path: str, port: int) -> Dict[str, str]:
    """Handle FTP file transfer"""
    ftp = ftplib.FTP()
    
    try:
        # Connect to FTP server
        ftp.connect(host, port, timeout=30)
        ftp.login(username, password)
        
        downloaded_files = []
        
        # Check if remote_path is a file or directory
        try:
            # Try to change to the path as a directory
            current_dir = ftp.pwd()
            ftp.cwd(remote_path)
            is_directory = True
            ftp.cwd(current_dir)  # Change back
        except:
            is_directory = False
        
        if not is_directory:
            # Download single file
            filename = os.path.basename(remote_path)
            local_path = os.path.join(UPLOAD_DIR, filename)
            with open(local_path, 'wb') as local_file:
                ftp.retrbinary(f'RETR {remote_path}', local_file.write)
            downloaded_files.append((filename, local_path))
        else:
            # Download all files from directory
            ftp.cwd(remote_path)
            files = ftp.nlst()
            for filename in files:
                local_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    with open(local_path, 'wb') as local_file:
                        ftp.retrbinary(f'RETR {filename}', local_file.write)
                    downloaded_files.append((filename, local_path))
                except Exception as e:
                    print(f"Warning: Failed to download {filename}: {e}")
        
        # Process downloaded files
        return _process_downloaded_files(downloaded_files, "FTP", host, remote_path)
        
    finally:
        ftp.quit()

def _process_downloaded_files(downloaded_files: list, protocol: str, host: str, remote_path: str) -> Dict[str, str]:
    """Process downloaded files and return structured data"""
    if not downloaded_files:
        raise ValueError("No files were downloaded")
    
    all_data = []
    file_info = []
    
    for filename, local_path in downloaded_files:
        file_info.append({
            "filename": filename,
            "size": os.path.getsize(local_path),
            "path": local_path
        })
        
        # Try to read file as CSV/text if possible
        try:
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in ['.csv', '.txt']:
                # Try reading as CSV
                df = pd.read_csv(local_path, dtype=str)
                df['source_file'] = filename
                all_data.extend(df.to_dict(orient="records"))
            elif file_ext == '.json':
                # Try reading as JSON
                df = pd.read_json(local_path)
                df['source_file'] = filename
                all_data.extend(df.to_dict(orient="records"))
            else:
                # For other file types, just record metadata
                all_data.append({
                    "filename": filename,
                    "file_type": file_ext,
                    "size": os.path.getsize(local_path),
                    "message": "File downloaded but not parsed"
                })
        except Exception as e:
            # If parsing fails, just record the file info
            all_data.append({
                "filename": filename,
                "error": str(e),
                "message": "File downloaded but parsing failed"
            })
    
    # Create summary DataFrame
    if all_data:
        df = pd.DataFrame(all_data)
    else:
        df = pd.DataFrame([{"message": "Files downloaded but no data extracted"}])
    
    # Replace NaN with None for consistent handling
    df = df.where(pd.notna(df), None)
    
    print(f"Successfully downloaded {len(downloaded_files)} files via {protocol}")
    print(f"Host: {host}, Remote path: {remote_path}")
    print(f"Files: {[f[0] for f in downloaded_files]}")
    
    return {
        "data": df.to_dict(orient="records"),
        "filename": f"{protocol.lower()}_{host}_{len(downloaded_files)}_files.csv",
        "protocol": protocol,
        "host": host,
        "remote_path": remote_path,
        "files_downloaded": len(downloaded_files),
        "file_info": file_info
    }