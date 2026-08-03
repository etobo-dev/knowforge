locals {
  project = jsondecode(file("${path.module}/../config/project.json"))

  project_name              = local.project.project_name
  aws_region                = local.project.aws.region
  back_ecr_repository       = local.project.back.ecr_repository
  back_lambda_name = local.project.back.lambda_name
  documents_bucket          = local.project.storage.documents_bucket
}
