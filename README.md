![](housing-diagram.png)
<br /><br />
For mapping and data analysis see: https://colab.research.google.com/drive/1E2Au6yILMcWZXiBfcg6qhS6csXFvWYcI?usp=sharing

<br /><br />
What could be improved:
- First Lambda could interact directly with the Lambda leading to DynamoDB and API Gateway should be there only for requests from outside of AWS.
- Instead of interacting the RDS directly, local host could send requests to a Lambda via a new API Gateway. This would improve the database security, but make it difficult to use MySQL workbench.
- Local host could be completely removed from the application and an EC2 instance or a AWS SageMaker could be used instead. However, this would increase the costs.
