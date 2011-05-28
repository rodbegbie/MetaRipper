import Util.Barcode as Barcode
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
            result = Barcode.validateBarcode(bc)
            self.assertEqual(result, expectedResult)

class BadValues(unittest.TestCase):
    def testTooShort(self):
        for i in range(0,11):
            bc = "0" * i
            result = Barcode.validateBarcode(bc)
            self.assertFalse(result)
        
    def testTooLong(self):
        for i in range(14,20):
            bc = "0" * i
            result = Barcode.validateBarcode(bc)
            self.assertFalse(result)
            
    def testNonNumeric(self):
        for bc in ("0000000000X", "Barcode123456"):
            result = Barcode.validateBarcode(bc)
            self.assertFalse(result)        
            
if __name__ == "__main__":
    unittest.main()