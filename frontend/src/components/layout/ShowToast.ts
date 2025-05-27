export function showToast(
    message: string,
    type: "success" | "error" | "info" | "warning" = "info"
  ) {
    const colors = {
      success: "alert-success",
      error: "alert-error",
      warning: "alert-warning",
      info: "alert-info",
    };
  
    const div = document.createElement("div");
    div.className = `toast z-[1000] fixed right-4 bottom-4`;
    div.innerHTML = `
        <div class="alert ${colors[type]} alert-soft shadow-lg text-lg">
          <span>${message}</span>
        </div>
      `;
  
    document.body.appendChild(div);
  
    setTimeout(() => {
      div.remove();
    }, 3000);
  }