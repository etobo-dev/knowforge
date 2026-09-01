variable "aws_profile" {
  type    = string
  default = "knowforge"
}

variable "lambda_architecture" {
  type    = string
  default = "x86_64"
}

variable "database_url" {
  type        = string
  sensitive   = true
  description = "PostgreSQL connection string for the backend."
}

variable "openai_api_key" {
  type        = string
  sensitive   = true
  description = "OpenAI API key used by the RAG pipeline."
}

variable "cors_allowed_origins" {
  type = list(string)
  default = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://knowforge.etobo.tech",
  ]
  description = "Origins allowed to call the backend API."
}

variable "google_oauth_client_id" {
  type        = string
  sensitive   = true
  description = "Google OAuth 2.0 client ID for Cognito Google IdP federation."
}

variable "google_oauth_client_secret" {
  type        = string
  sensitive   = true
  description = "Google OAuth 2.0 client secret for Cognito Google IdP federation."
}

variable "cognito_callback_urls" {
  type = list(string)
  default = [
    "http://localhost:3000/auth/callback",
    "http://127.0.0.1:3000/auth/callback",
    "https://knowforge.etobo.tech/auth/callback",
  ]
  description = "OAuth redirect URIs registered on the Cognito app client."
}

variable "cognito_logout_urls" {
  type = list(string)
  default = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://knowforge.etobo.tech",
  ]
  description = "Sign-out redirect URIs registered on the Cognito app client."
}
