1.main.tf: Contains the core resource definitions (IAM role, security group, EC2 instance).
2.variables.tf: Declares all the input variables, similar to the Parameters section in your CloudFormation template.
3.outputs.tf: Defines the stack outputs, just like the Outputs section in your template.
Here are the new files. You can save them in a new directory and run terraform init, terraform plan, and terraform apply.

1. New File: main.tf
This file is the core of your Terraform configuration, defining the AWS resources to be created.

2. New File: variables.tf
This file defines the inputs for your configuration, similar to the Parameters section in CloudFormation. You should edit the default values here before running Terraform.

3. New File: outputs.tf
This file is identical to the one you provided, as it correctly defines the outputs for the project.

How to Use These New Files

1.Create a Directory: Make a new, empty directory for your Terraform project.

2.Save the Files: Save the three code blocks above into that directory as main.tf, variables.tf, and outputs.tf.

3.Update variables.tf: Edit the default values in variables.tf to match your AWS environment (VPC, Subnet, IP address, and Key Pair name).

4.Initialize: Open a terminal in that directory and run terraform init.

5.Plan: Run terraform plan to see what will be created.
Apply: Run terraform apply to build the infrastructure.

