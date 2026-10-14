const API_BASE_URL = "http://127.0.0.1:8000";

export async function getPolicyChanges(policyName) {
  const url = `${API_BASE_URL}/policies/${encodeURIComponent(policyName)}/changes`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch policy changes (${response.status})`);
  }

  return response.json();
}

export async function askPolicyQuestion(policyName, question) {
  const params = new URLSearchParams({ question });

  const url = `${API_BASE_URL}/policies/${encodeURIComponent(policyName)}/ask?${params}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to get an answer (${response.status})`);
  }

  return response.json();
}