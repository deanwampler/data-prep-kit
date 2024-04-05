import os

from data_processing.data_access import DataAccessLocal
from noop_transform import NOOPTransform


# create parameters
input_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test-data", "input"))

noop_params = {"sleep_sec": 1}
if __name__ == "__main__":
    # Here we show how to run outside of ray
    # Create and configure the transform.
    transform = NOOPTransform(noop_params)
    # Use the local data access to read a parquet table.
    data_access = DataAccessLocal()
    table = data_access.get_table(os.path.join(input_folder, "test1.parquet"))
    print(f"input table: {table}")
    # Transform the table
    table_list, metadata = transform.transform(table)
    print(f"\noutput table: {table_list}")
    print(f"output metadata : {metadata}")
