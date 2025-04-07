export async function submitWorkflow(payload: any) {
  const res = await fetch("/api/workflows", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  console.log("submitWorkflow", payload, res)

  if (!res.ok) {
    throw new Error("Failed to submit workflow")
  }

  return res.json()
}
