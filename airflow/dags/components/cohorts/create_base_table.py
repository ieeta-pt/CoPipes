import pandas as pd
from typing import Dict, List, Any, Optional
from airflow.utils.log.logging_mixin import LoggingMixin

def create_mapping(
    columns_dst: List[str],
    table: str,
    harmonizer_adhoc: Any = None,
    column_mapper: Dict[str, str] = None,
    common_harmonizer_methods: Optional[Any] = None,
    config: Optional[bool] = False,
    **kwargs
) -> pd.DataFrame:

    logger = LoggingMixin().log
    ti = kwargs['ti']
    cohort = ti.xcom_pull(key='csv_data', task_ids='read_csv')

    if not cohort:
        logger.error("No data received from read_csv task.")
        raise ValueError("No data received from read_csv task.")

    cohort = pd.DataFrame(cohort)

    size = len(cohort)

    mapping = pd.DataFrame(index=range(size), columns=columns_dst)

    for element in columns_dst:
        source_field = None

        if (element in column_mapper):
            source_field = column_mapper.get(element)
    
        mapping[element] = None  # Default value    
        method_name = f"set_{table}_{element}"
        
        if hasattr(harmonizer_adhoc, method_name):
            # Ad hoc method exists
            mapping[element] = _apply_harmonizer_method(
                harmonizer_adhoc, method_name, cohort, source_field
            )
        elif (common_harmonizer_methods 
              and hasattr(common_harmonizer_methods, method_name) 
              and config.adhocmethods):
            # Common harmonizer method exists
            mapping[element] = _apply_standard_adhoc_method(
                common_harmonizer_methods, method_name, cohort, source_field
            )
        elif source_field in cohort:  # Direct mapping
            mapping.loc[:, element] = cohort[source_field].values

    ti.xcom_push(key='mapping', value=mapping.to_dict())
    
def cohort_filter(
    cohort: pd.DataFrame,
    table: str,
    harmonizer_adhoc: Any
) -> pd.DataFrame:
    """Apply cohort-specific filters if they exist.
    
    Args:
        cohort: The data frame to filter
        table: Name of the table being processed
        harmonizer_adhoc: Object containing filter methods
    
    Returns:
        pd.DataFrame: Filtered data frame
    """
    method_name = f"filter_{table}"
    if hasattr(harmonizer_adhoc, method_name):
        return getattr(harmonizer_adhoc, method_name)(cohort)
    return cohort

def _apply_harmonizer_method(
    harmonizer: Any,
    method_name: str,
    cohort: pd.DataFrame,
    source_field: Optional[str]
) -> Any:
    """Apply a harmonization method to the data.
    
    Args:
        harmonizer: Object containing the harmonization method
        method_name: Name of the method to call
        cohort: Source data
        source_field: Name of the source field
    
    Returns:
        Harmonized data
    """
    source_data = cohort[source_field] if source_field in cohort else None
    return getattr(harmonizer, method_name)(source_data)

def _apply_standard_adhoc_method(
    harmonizer: Any,
    method_name: str,
    cohort: pd.DataFrame,
    source_field: Optional[str]
) -> Any:
    """Apply a standard ad-hoc harmonization method.
    
    Args:
        harmonizer: Object containing the harmonization method
        method_name: Name of the method to call
        cohort: Source data
        source_field: Name of the source field
    
    Returns:
        Harmonized data
        
    Raises:
        Exception: If the method fails or the field is not properly mapped
    """
    try:
        source_data = cohort[source_field] if source_field in cohort else None
        return getattr(harmonizer, method_name)(source_data)
    except Exception as e:
        raise Exception(
            f"Error processing field '{source_field}' with method '{method_name}'. "
            "Verify that the concept is properly mapped in Usagi."
        ) from e