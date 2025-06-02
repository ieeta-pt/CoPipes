// taskRegistry.ts
import { TaskRegistry } from "@/components/airflow-tasks/types"
import { BaseTask } from "@/components/airflow-tasks/BaseTask"

export const Registry: TaskRegistry = {
  "CSV": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "filename", 
        value: "", 
        type: "file",
        placeholder: "File to read",
        required: true,
        validation: { message: "Filename is required" }
      },
      { 
        name: "file separation", 
        value: "Comma", 
        type: "select",
        options: ["Comma", "Semicolon", "Tab"],
        placeholder: "Select file separator",
        required: false
      }
    ],
    component: BaseTask,
  },
  "JSON": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "source", 
        value: "", 
        type: "string",
        placeholder: "JSON file path or API endpoint",
        required: true,
        validation: { message: "JSON source is required" }
      },
      { 
        name: "json path", 
        value: "", 
        type: "string",
        placeholder: "JSONPath expression to extract data (e.g., $.data[*])",
        required: false
      },
      { 
        name: "flatten nested", 
        value: "True", 
        type: "boolean",
        placeholder: "Flatten nested JSON objects",
        required: false
      }
    ],
    component: BaseTask,
  },
  "XML": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "source", 
        value: "", 
        type: "string",
        placeholder: "XML file path or URL",
        required: true,
        validation: { message: "XML source is required" }
      },
      { 
        name: "xpath", 
        value: "", 
        type: "string",
        placeholder: "XPath expression to extract elements",
        required: false
      },
      { 
        name: "namespaces", 
        value: "", 
        type: "string",
        placeholder: "XML namespaces (JSON format)",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Database Query": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "connection", 
        value: "", 
        type: "task_reference",
        placeholder: "Database connection (Create connection result)",
        required: true,
        validation: { message: "Database connection is required" }
      },
      { 
        name: "query", 
        value: "", 
        type: "string",
        placeholder: "SQL query to execute",
        required: true,
        validation: { message: "SQL query is required" }
      },
      { 
        name: "parameters", 
        value: "", 
        type: "string",
        placeholder: "Query parameters (JSON format)",
        required: false
      }
    ],
    component: BaseTask,
  },
  "REST API": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "endpoint", 
        value: "", 
        type: "string",
        placeholder: "API endpoint URL",
        required: true,
        validation: { message: "API endpoint is required" }
      },
      { 
        name: "method", 
        value: "GET", 
        type: "select",
        options: ["GET", "POST", "PUT", "DELETE"],
        placeholder: "HTTP method",
        required: false
      },
      { 
        name: "headers", 
        value: "", 
        type: "string",
        placeholder: "HTTP headers (JSON format)",
        required: false
      },
      { 
        name: "auth token", 
        value: "", 
        type: "string",
        placeholder: "Authorization token",
        required: false
      },
      { 
        name: "pagination", 
        value: "False", 
        type: "boolean",
        placeholder: "Handle paginated responses",
        required: false
      }
    ],
    component: BaseTask,
  },
  "FTP/SFTP": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "host", 
        value: "", 
        type: "string",
        placeholder: "FTP/SFTP server host",
        required: true,
        validation: { message: "Host is required" }
      },
      { 
        name: "username", 
        value: "", 
        type: "string",
        placeholder: "Username",
        required: true,
        validation: { message: "Username is required" }
      },
      { 
        name: "password", 
        value: "", 
        type: "string",
        placeholder: "Password",
        required: true,
        validation: { message: "Password is required" }
      },
      { 
        name: "remote path", 
        value: "", 
        type: "string",
        placeholder: "Remote file/directory path",
        required: true,
        validation: { message: "Remote path is required" }
      },
      { 
        name: "protocol", 
        value: "SFTP", 
        type: "select",
        options: ["FTP", "SFTP"],
        placeholder: "Transfer protocol",
        required: false
      },
      { 
        name: "port", 
        value: "22", 
        type: "string",
        placeholder: "Port number",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Port must be a number" }
      }
    ],
    component: BaseTask,
  },
  "Web Scraping": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "url", 
        value: "", 
        type: "string",
        placeholder: "Website URL to scrape",
        required: true,
        validation: { message: "URL is required" }
      },
      { 
        name: "css selector", 
        value: "", 
        type: "string",
        placeholder: "CSS selector for target elements",
        required: false
      },
      { 
        name: "xpath", 
        value: "", 
        type: "string",
        placeholder: "XPath expression for target elements",
        required: false
      },
      { 
        name: "wait time", 
        value: "3", 
        type: "string",
        placeholder: "Seconds to wait for page load",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Must be a number" }
      },
      { 
        name: "use browser", 
        value: "False", 
        type: "boolean",
        placeholder: "Use headless browser for JavaScript content",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Data Cleaning": {
    type: "Transformation",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to clean (extraction result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "remove duplicates", 
        value: "True", 
        type: "boolean",
        placeholder: "Remove duplicate records",
        required: false
      },
      { 
        name: "handle missing values", 
        value: "drop", 
        type: "select",
        options: ["drop", "mean", "median", "mode", "forward_fill", "backward_fill"],
        placeholder: "Strategy for missing values",
        required: false
      },
      { 
        name: "outlier detection", 
        value: "zscore", 
        type: "select",
        options: ["none", "zscore", "iqr", "isolation_forest"],
        placeholder: "Outlier detection method",
        required: false
      },
      { 
        name: "outlier threshold", 
        value: "3", 
        type: "string",
        placeholder: "Threshold for outlier detection",
        required: false,
        validation: { pattern: "^[0-9]+(\\.[0-9]+)?$", message: "Must be a valid number" }
      }
    ],
    component: BaseTask,
  },
  "Data Filtering": {
    type: "Transformation",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to filter (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "filter conditions", 
        value: "", 
        type: "string",
        placeholder: "Filter conditions (e.g., age > 18 AND status = 'active')",
        required: true,
        validation: { message: "Filter conditions are required" }
      },
      { 
        name: "columns to keep", 
        value: "", 
        type: "string",
        placeholder: "Columns to keep (separated by commas, leave empty for all)",
        required: false
      },
      { 
        name: "limit rows", 
        value: "", 
        type: "string",
        placeholder: "Maximum number of rows to return",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Must be a positive integer" }
      }
    ],
    component: BaseTask,
  },
  "Data Aggregation": {
    type: "Transformation",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to aggregate (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "group by columns", 
        value: "", 
        type: "string",
        placeholder: "Columns to group by (separated by commas)",
        required: true,
        validation: { message: "Group by columns are required" }
      },
      { 
        name: "aggregation functions", 
        value: "", 
        type: "string",
        placeholder: "Aggregations (e.g., sum(sales), avg(price), count(*))",
        required: true,
        validation: { message: "Aggregation functions are required" }
      },
      { 
        name: "having conditions", 
        value: "", 
        type: "string",
        placeholder: "HAVING clause conditions (optional)",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Data Join": {
    type: "Transformation",
    defaultConfig: [
      { 
        name: "left data", 
        value: "", 
        type: "task_reference",
        placeholder: "Left dataset (extraction or transformation result)",
        required: true,
        validation: { message: "Left data is required" }
      },
      { 
        name: "right data", 
        value: "", 
        type: "task_reference",
        placeholder: "Right dataset (extraction or transformation result)",
        required: true,
        validation: { message: "Right data is required" }
      },
      { 
        name: "join type", 
        value: "inner", 
        type: "select",
        options: ["inner", "left", "right", "outer", "cross"],
        placeholder: "Type of join operation",
        required: false
      },
      { 
        name: "join keys", 
        value: "", 
        type: "string",
        placeholder: "Join keys (e.g., left.id = right.customer_id)",
        required: true,
        validation: { message: "Join keys are required" }
      }
    ],
    component: BaseTask,
  },
  "Data Pivot": {
    type: "Transformation",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to pivot (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "index columns", 
        value: "", 
        type: "string",
        placeholder: "Columns to use as row index (separated by commas)",
        required: true,
        validation: { message: "Index columns are required" }
      },
      { 
        name: "pivot columns", 
        value: "", 
        type: "string",
        placeholder: "Columns to pivot into new columns",
        required: true,
        validation: { message: "Pivot columns are required" }
      },
      { 
        name: "value columns", 
        value: "", 
        type: "string",
        placeholder: "Columns containing values to aggregate",
        required: true,
        validation: { message: "Value columns are required" }
      },
      { 
        name: "aggregation function", 
        value: "sum", 
        type: "select",
        options: ["sum", "mean", "count", "min", "max", "std"],
        placeholder: "Aggregation function for values",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Data Sorting": {
    type: "Transformation",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to sort (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "sort columns", 
        value: "", 
        type: "string",
        placeholder: "Columns to sort by (separated by commas)",
        required: true,
        validation: { message: "Sort columns are required" }
      },
      { 
        name: "sort order", 
        value: "asc", 
        type: "select",
        options: ["asc", "desc", "custom"],
        placeholder: "Sort order",
        required: false
      },
      { 
        name: "custom order", 
        value: "", 
        type: "string",
        placeholder: "Custom sort order (e.g., asc,desc,asc)",
        required: false
      }
    ],
    component: BaseTask,
  },
  "To key value": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data to reorganize (CSV extraction result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "fixed columns", 
        value: "", 
        type: "string", 
        placeholder: "List of fixed columns names (separated by commas)",
        required: false
      },
      { 
        name: "measurement columns", 
        value: "", 
        type: "string", 
        placeholder: "List of measurement columns (separated by commas)",
        required: false
      },
    ],
    component: BaseTask,
  },
  "Harmonize": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data to harmonize (To key value result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "mappings", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data mappings (CSV extraction result or file)",
        required: true,
        validation: { message: "Mappings are required" }
      },
      { 
        name: "adhoc harmonization", 
        value: "False", 
        type: "boolean",
        placeholder: "Enable ad-hoc harmonization rules",
        required: false
      },
    ],
    component: BaseTask,
  },
  "Migrate": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { 
        name: "person data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data for personal information table (CSV extraction result)",
        required: true,
        validation: { message: "Person data is required" }
      },
      { 
        name: "observation data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data for observation table (Harmonize result)",
        required: true,
        validation: { message: "Observation data is required" }
      },
      { 
        name: "mappings", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data mappings (CSV extraction result or file)",
        required: true,
        validation: { message: "Mappings are required" }
      },
      { 
        name: "adhoc migration", 
        value: "False", 
        type: "boolean",
        placeholder: "Enable ad-hoc migration rules",
        required: false
      },
    ],
    component: BaseTask,
  },
  "Create connection": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { 
        name: "connection id", 
        value: "my_postgres", 
        type: "string",
        placeholder: "Connection identifier",
        required: false
      },
      { 
        name: "host", 
        value: "postgres", 
        type: "string",
        placeholder: "Database host",
        required: false
      },
      { 
        name: "schema", 
        value: "airflow", 
        type: "string",
        placeholder: "Database schema",
        required: false
      },
      { 
        name: "login", 
        value: "airflow", 
        type: "string",
        placeholder: "Database username",
        required: false
      },
      { 
        name: "password", 
        value: "airflow", 
        type: "string",
        placeholder: "Database password",
        required: false
      },
      { 
        name: "port", 
        value: "5432", 
        type: "string",
        placeholder: "Database port",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Port must be a number" }
      }
    ],
    component: BaseTask,
  },
  "Create table": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { 
        name: "columns", 
        value: "", 
        type: "string", 
        placeholder: "List of columns (separated by commas)",
        required: true,
        validation: { message: "Column list is required" }
      },
      { 
        name: "table name", 
        value: "", 
        type: "string", 
        placeholder: "My table",
        required: true,
        validation: { message: "Table name is required" }
      },
    ],
    component: BaseTask,
  },
  "Write to DB": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Table contents (Migrate result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "table name", 
        value: "", 
        type: "string", 
        placeholder: "My table",
        required: true,
        validation: { message: "Table name is required" }
      },
      { 
        name: "connection id", 
        value: "my_postgres", 
        type: "string",
        placeholder: "Connection identifier",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Batch Load": {
    type: "Loading",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to load (transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "destination", 
        value: "", 
        type: "string",
        placeholder: "Destination (database, file path, cloud storage)",
        required: true,
        validation: { message: "Destination is required" }
      },
      { 
        name: "load mode", 
        value: "append", 
        type: "select",
        options: ["append", "overwrite", "upsert"],
        placeholder: "How to handle existing data",
        required: false
      },
      { 
        name: "batch size", 
        value: "1000", 
        type: "string",
        placeholder: "Number of records per batch",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Must be a positive integer" }
      },
      { 
        name: "parallel workers", 
        value: "1", 
        type: "string",
        placeholder: "Number of parallel load processes",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Must be a positive integer" }
      }
    ],
    component: BaseTask,
  },
  "Incremental Load": {
    type: "Loading",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to load incrementally (transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "destination", 
        value: "", 
        type: "string",
        placeholder: "Destination table or location",
        required: true,
        validation: { message: "Destination is required" }
      },
      { 
        name: "key columns", 
        value: "", 
        type: "string",
        placeholder: "Columns to identify unique records (separated by commas)",
        required: true,
        validation: { message: "Key columns are required" }
      },
      { 
        name: "timestamp column", 
        value: "", 
        type: "string",
        placeholder: "Column to track record updates",
        required: false
      },
      { 
        name: "last sync timestamp", 
        value: "", 
        type: "string",
        placeholder: "Last synchronization timestamp",
        required: false
      },
      { 
        name: "delete detection", 
        value: "False", 
        type: "boolean",
        placeholder: "Detect and handle deleted records",
        required: false
      }
    ],
    component: BaseTask,
  },
  "File Export": {
    type: "Loading",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to export (transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "file path", 
        value: "", 
        type: "string",
        placeholder: "Output file path",
        required: true,
        validation: { message: "File path is required" }
      },
      { 
        name: "file format", 
        value: "csv", 
        type: "select",
        options: ["csv", "json", "parquet", "xlsx", "xml"],
        placeholder: "Export file format",
        required: false
      },
      { 
        name: "compression", 
        value: "none", 
        type: "select",
        options: ["none", "gzip", "bzip2", "snappy"],
        placeholder: "File compression",
        required: false
      },
      { 
        name: "include header", 
        value: "True", 
        type: "boolean",
        placeholder: "Include column headers",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Data Preprocessing": {
    type: "Analysis",
    subtype: "Machine Learning",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to preprocess (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "target column", 
        value: "", 
        type: "string",
        placeholder: "Name of the target variable column",
        required: false
      },
      { 
        name: "feature columns", 
        value: "", 
        type: "string",
        placeholder: "List of feature column names (separated by commas)",
        required: false
      },
      { 
        name: "handle missing", 
        value: "True", 
        type: "boolean",
        placeholder: "Handle missing values",
        required: false
      },
      { 
        name: "missing strategy", 
        value: "auto", 
        type: "select",
        options: ["auto", "mean", "median", "mode", "knn"],
        placeholder: "Strategy for handling missing values",
        required: false
      },
      { 
        name: "scale features", 
        value: "True", 
        type: "boolean",
        placeholder: "Apply feature scaling",
        required: false
      },
      { 
        name: "scaling method", 
        value: "standard", 
        type: "select",
        options: ["standard", "minmax", "robust"],
        placeholder: "Feature scaling method",
        required: false
      },
      { 
        name: "encode categorical", 
        value: "True", 
        type: "boolean",
        placeholder: "Encode categorical variables",
        required: false
      },
      { 
        name: "categorical encoding", 
        value: "auto", 
        type: "select",
        options: ["auto", "onehot", "label", "ordinal"],
        placeholder: "Categorical encoding method",
        required: false
      },
      { 
        name: "feature selection", 
        value: "False", 
        type: "boolean",
        placeholder: "Perform feature selection",
        required: false
      },
      { 
        name: "remove outliers", 
        value: "False", 
        type: "boolean",
        placeholder: "Remove outliers from data",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Model Training": {
    type: "Analysis",
    subtype: "Machine Learning",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Training data (Data Preprocessing result)",
        required: true,
        validation: { message: "Training data is required" }
      },
      { 
        name: "target column", 
        value: "", 
        type: "string",
        placeholder: "Name of the target variable column",
        required: true,
        validation: { message: "Target column is required" }
      },
      { 
        name: "feature columns", 
        value: "", 
        type: "string",
        placeholder: "List of feature column names (separated by commas)",
        required: false
      },
      { 
        name: "model type", 
        value: "random_forest", 
        type: "select",
        options: ["random_forest", "logistic_regression", "svm", "linear_regression"],
        placeholder: "Machine learning algorithm",
        required: false
      },
      { 
        name: "task type", 
        value: "classification", 
        type: "select",
        options: ["classification", "regression"],
        placeholder: "Type of machine learning task",
        required: false
      },
      { 
        name: "test size", 
        value: "0.2", 
        type: "string",
        placeholder: "Proportion of data for testing (0.0-1.0)",
        required: false,
        validation: { pattern: "^0\\.[0-9]+$|^1\\.0$", message: "Must be a decimal between 0.0 and 1.0" }
      },
      { 
        name: "random state", 
        value: "42", 
        type: "string",
        placeholder: "Random seed for reproducibility",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Must be a positive integer" }
      },
      { 
        name: "hyperparameter tuning", 
        value: "False", 
        type: "boolean",
        placeholder: "Perform hyperparameter tuning",
        required: false
      },
      { 
        name: "cross validation", 
        value: "True", 
        type: "boolean",
        placeholder: "Perform cross-validation",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Model Evaluation": {
    type: "Analysis",
    subtype: "Machine Learning",
    defaultConfig: [
      { 
        name: "model path", 
        value: "", 
        type: "string",
        placeholder: "Path to the saved model file",
        required: true,
        validation: { message: "Model path is required" }
      },
      { 
        name: "test data", 
        value: "", 
        type: "task_reference",
        placeholder: "Test dataset (Data Preprocessing result)",
        required: true,
        validation: { message: "Test data is required" }
      },
      { 
        name: "generate plots", 
        value: "True", 
        type: "boolean",
        placeholder: "Generate evaluation plots",
        required: false
      },
      { 
        name: "save predictions", 
        value: "True", 
        type: "boolean",
        placeholder: "Save predictions to file",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Deploy Model": {
    type: "Analysis",
    subtype: "Machine Learning",
    defaultConfig: [
      { 
        name: "model path", 
        value: "", 
        type: "string",
        placeholder: "Path to the trained model file",
        required: true,
        validation: { message: "Model path is required" }
      },
      { 
        name: "evaluation results", 
        value: "", 
        type: "task_reference",
        placeholder: "Model evaluation results",
        required: true,
        validation: { message: "Evaluation results are required" }
      },
      { 
        name: "model name", 
        value: "", 
        type: "string",
        placeholder: "Name for the deployed model",
        required: false
      },
      { 
        name: "performance threshold", 
        value: "", 
        type: "string",
        placeholder: "Minimum performance threshold for deployment",
        required: false,
        validation: { pattern: "^[0-9]+(\\.[0-9]+)?$", message: "Must be a valid number" }
      },
      { 
        name: "metric name", 
        value: "accuracy", 
        type: "select",
        options: ["accuracy", "precision", "recall", "f1_score", "r2_score"],
        placeholder: "Metric to check against threshold",
        required: false
      },
      { 
        name: "backup existing", 
        value: "True", 
        type: "boolean",
        placeholder: "Backup existing production model",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Rollback Model": {
    type: "Analysis",
    subtype: "Machine Learning",
    defaultConfig: [
      { 
        name: "model name", 
        value: "", 
        type: "string",
        placeholder: "Name of the model to rollback",
        required: true,
        validation: { message: "Model name is required" }
      },
      { 
        name: "deployment directory", 
        value: "/shared_data/production_models", 
        type: "string",
        placeholder: "Directory containing production models",
        required: false
      }
    ],
    component: BaseTask,
  },
  "List Deployed Models": {
    type: "Analysis",
    subtype: "Machine Learning",
    defaultConfig: [
      { 
        name: "deployment directory", 
        value: "/shared_data/production_models", 
        type: "string",
        placeholder: "Directory containing production models",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Execute Notebook": {
    type: "Analysis",
    subtype: "Jupyter",
    defaultConfig: [
      { 
        name: "input notebook path", 
        value: "", 
        type: "string",
        placeholder: "Path to input notebook file",
        required: true,
        validation: { message: "Input notebook path is required" }
      },
      { 
        name: "output directory", 
        value: "/shared_data/notebooks/output", 
        type: "string",
        placeholder: "Directory to save executed notebook",
        required: false
      },
      { 
        name: "parameters", 
        value: "", 
        type: "string",
        placeholder: "Parameters to pass to notebook (JSON format)",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Descriptive Statistics": {
    type: "Analysis",
    subtype: "Statistical",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to analyze (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "target columns", 
        value: "", 
        type: "string",
        placeholder: "Columns to analyze (separated by commas, leave empty for all numeric)",
        required: false
      },
      { 
        name: "include", 
        value: "all", 
        type: "select",
        options: ["all", "number", "object", "datetime"],
        placeholder: "Data types to include in analysis",
        required: false
      },
      { 
        name: "percentiles", 
        value: "0.25,0.5,0.75", 
        type: "string",
        placeholder: "Percentiles to calculate (separated by commas)",
        required: false
      },
      { 
        name: "generate plots", 
        value: "True", 
        type: "boolean",
        placeholder: "Generate distribution plots",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Data Correlation": {
    type: "Analysis",
    subtype: "Statistical",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to analyze (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "method", 
        value: "pearson", 
        type: "select",
        options: ["pearson", "kendall", "spearman"],
        placeholder: "Correlation method",
        required: false
      },
      { 
        name: "target columns", 
        value: "", 
        type: "string",
        placeholder: "Columns to include (separated by commas, leave empty for all numeric)",
        required: false
      },
      { 
        name: "threshold", 
        value: "0.5", 
        type: "string",
        placeholder: "Correlation threshold for highlighting",
        required: false,
        validation: { pattern: "^0\\.[0-9]+$|^1\\.0$", message: "Must be between 0.0 and 1.0" }
      },
      { 
        name: "generate heatmap", 
        value: "True", 
        type: "boolean",
        placeholder: "Generate correlation heatmap",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Data Visualization": {
    type: "Analysis",
    subtype: "Visualization",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference",
        placeholder: "Data to visualize (extraction or transformation result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "chart type", 
        value: "scatter", 
        type: "select",
        options: ["scatter", "line", "bar", "histogram", "box", "heatmap", "pie"],
        placeholder: "Type of visualization",
        required: true,
        validation: { message: "Chart type is required" }
      },
      { 
        name: "x column", 
        value: "", 
        type: "string",
        placeholder: "Column for X-axis",
        required: false
      },
      { 
        name: "y column", 
        value: "", 
        type: "string",
        placeholder: "Column for Y-axis",
        required: false
      },
      { 
        name: "color column", 
        value: "", 
        type: "string",
        placeholder: "Column for color grouping",
        required: false
      },
      { 
        name: "title", 
        value: "", 
        type: "string",
        placeholder: "Chart title",
        required: false
      },
      { 
        name: "save format", 
        value: "png", 
        type: "select",
        options: ["png", "jpg", "svg", "pdf", "html"],
        placeholder: "Output format for chart",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Generate Report": {
    type: "Analysis",
    subtype: "Reporting",
    defaultConfig: [
      { 
        name: "data sources", 
        value: "", 
        type: "string",
        placeholder: "Data sources to include (task references separated by commas)",
        required: true,
        validation: { message: "Data sources are required" }
      },
      { 
        name: "report type", 
        value: "summary", 
        type: "select",
        options: ["summary", "detailed", "executive", "technical"],
        placeholder: "Type of report to generate",
        required: false
      },
      { 
        name: "template", 
        value: "default", 
        type: "string",
        placeholder: "Report template to use",
        required: false
      },
      { 
        name: "include charts", 
        value: "True", 
        type: "boolean",
        placeholder: "Include data visualizations",
        required: false
      },
      { 
        name: "output format", 
        value: "pdf", 
        type: "select",
        options: ["pdf", "html", "docx", "xlsx"],
        placeholder: "Report output format",
        required: false
      },
      { 
        name: "schedule", 
        value: "", 
        type: "string",
        placeholder: "Automated report schedule (cron format)",
        required: false
      }
    ],
    component: BaseTask,
  },
  "Send Notification": {
    type: "Utils",
    defaultConfig: [
      { 
        name: "recipient", 
        value: "", 
        type: "string",
        placeholder: "Email address or notification target",
        required: true,
        validation: { message: "Recipient is required" }
      },
      { 
        name: "subject", 
        value: "Workflow Notification", 
        type: "string",
        placeholder: "Notification subject",
        required: false
      },
      { 
        name: "message", 
        value: "", 
        type: "string",
        placeholder: "Notification message content",
        required: true,
        validation: { message: "Message content is required" }
      },
      { 
        name: "notification type", 
        value: "email", 
        type: "select",
        options: ["email", "slack", "webhook", "sms"],
        placeholder: "Type of notification to send",
        required: false
      },
      { 
        name: "attach results", 
        value: "False", 
        type: "boolean",
        placeholder: "Include workflow results in notification",
        required: false
      }
    ],
    component: BaseTask,
  },
}
