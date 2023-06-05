import cast_upgrade_1_6_13 # @UnusedImport
import unittest
import tempfile
from cast.application.test import run
from cast.application import create_engine

class TestIntegration(unittest.TestCase):

    def test_basic(self):
        myengine = create_engine("postgresql+pg8000://operator:CastAIP@localhost:2284/postgres")
        run(kb_name='com_vogella_junit_first_local', application_name='com.vogella.junit.first', engine=myengine)
                
if __name__ == "__main__":
    unittest.main()