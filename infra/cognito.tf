resource "aws_cognito_user_pool" "main" {
  name = "${local.project_name}-users"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Project = local.project_name
  }
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = local.cognito_domain_prefix
  user_pool_id = aws_cognito_user_pool.main.id
}

resource "aws_cognito_identity_provider" "google" {
  user_pool_id  = aws_cognito_user_pool.main.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    authorize_scopes = "openid email profile"
    client_id        = var.google_oauth_client_id
    client_secret    = var.google_oauth_client_secret
  }

  attribute_mapping = {
    email    = "email"
    name     = "name"
    username = "sub"
  }
}

resource "aws_cognito_user_pool_client" "web" {
  name         = "${local.project_name}-web"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]

  supported_identity_providers = ["Google"]

  callback_urls = var.cognito_callback_urls
  logout_urls   = var.cognito_logout_urls

  prevent_user_existence_errors = "ENABLED"
  enable_token_revocation       = true

  access_token_validity  = 60
  id_token_validity      = 60
  refresh_token_validity = 30

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  depends_on = [aws_cognito_identity_provider.google]
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID for JWT verification."
  value       = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN."
  value       = aws_cognito_user_pool.main.arn
}

output "cognito_app_client_id" {
  description = "Public Cognito app client ID for the web front end."
  value       = aws_cognito_user_pool_client.web.id
}

output "cognito_region" {
  description = "AWS region where the Cognito User Pool is deployed."
  value       = local.aws_region
}

output "cognito_issuer_url" {
  description = "JWT issuer URL for Cognito access tokens."
  value       = "https://cognito-idp.${local.aws_region}.amazonaws.com/${aws_cognito_user_pool.main.id}"
}

output "cognito_hosted_ui_domain" {
  description = "Cognito hosted UI domain (without scheme)."
  value       = "${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com"
}

output "cognito_hosted_ui_base_url" {
  description = "Base URL for Cognito hosted UI OAuth endpoints."
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com"
}

output "cognito_google_idp_redirect_uri" {
  description = "Redirect URI to register in the Google Cloud OAuth client."
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${local.aws_region}.amazoncognito.com/oauth2/idpresponse"
}
