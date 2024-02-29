from typing import Tuple

import pyarrow as pa
from data_processing_test.transform.transform_test import AbstractTransformTest
from ededup_transform import EdedupTransform


table = pa.Table.from_pydict({"name": pa.array(["Tom"]), "age": pa.array([23])})
expected_table = table
expected_metadata_list = [{"nfiles": 1, "nrows": 1}, {}]  # transform() result  # flush() result


class TestEdedupTransform(AbstractTransformTest):
    """
    Extends the super-class to define the test data for the tests defined there.
    The name of this class MUST begin with the word Test so that pytest recognizes it as a test class.
    """

    def get_test_transform_fixtures(self) -> list[Tuple]:
        fixtures = [
            # todo: copied from noop.  Needs attention to set real test data.
            # (EdedupTransform({"sleep": 0}), [table], [expected_table], expected_metadata_list),
            # (EdedupTransform({"sleep": 0}), [table], [expected_table], expected_metadata_list),
        ]
        return fixtures
