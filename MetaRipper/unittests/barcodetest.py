import Util.barcode as barcode
import unittest

class KnownValues(unittest.TestCase):
    knownValues = ( ("5020667344021", True),
                    ("609008103425", True),
                    ("5020667342423", True),
                    ("093624727224", True),
                    ("616892551621", True),
                    ("5019148610212", True),
                    ("5020664344021", False),
                    ("60900103425", False),
                    ("502066734243", False),
                    ("093624727225", False),
                    ("616982551621", False),
                    ("019148610212", False),
                  )
    
    def testKnownValues(self):
        for bc, expectedResult in self.knownValues:
            print bc
            result = barcode.validate_barcode(bc)
            self.assertEqual(result, expectedResult)

class BadValues(unittest.TestCase):
    def testTooShort(self):
        for i in range(0,11):
            bc = "0" * i
            result = barcode.validate_barcode(bc)
            self.assertFalse(result)
        
    def testTooLong(self):
        for i in range(14,20):
            bc = "0" * i
            result = barcode.validate_barcode(bc)
            self.assertFalse(result)
            
    def testNonNumeric(self):
        for bc in ("0000000000X", "BarCode1234"):
            result = barcode.validate_barcode(bc)
            self.assertFalse(result)        
            
if __name__ == "__main__":
    unittest.main()