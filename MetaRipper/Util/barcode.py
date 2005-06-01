import re

# Regex for 12 or 13 digits
valid_bc = re.compile("^[0-9]{12,13}$")

def validate_barcode(barcode):
    
    bc = str(barcode)
    if not valid_bc.match(bc):
        return False
        
    (a,b) = (0,0)
    
    bclen = len(bc)-1
    checkdigit = bc[bclen]
    
    for i in range(0,bclen):
        d = int(bc[i])
        if i%2:
            a += d
        else:
            b += d
#        print (a,b,i,d)
    
    if bclen % 2:
        b = b * 3
    else:
        a = a * 3
    
    checksum = a + b
    checksum = checksum % 10
    checksum = 10 - checksum
    if checksum == 10:
        checksum = 0
#    print checksum
    
    return str(checksum) == checkdigit
