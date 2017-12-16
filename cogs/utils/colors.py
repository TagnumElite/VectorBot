class color:
    attributes = {
        'normal': '0',
        'bold': '1',
        'underline': '4',
        'blink': '5',
        'reverse video': '7',
        'invisible': '8'
    }
    
    fore = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37'
    }
    
    back = {
        'black': '40',
        'red': '41',
        'green': '42',
        'yellow': '43',
        'blue': '44',
        'magenta': '45',
        'cyan': '46',
        'white': '47'
    }
    
    def disable(self):
        self.attributes = {
            'normal': '',
            'bold': '',
            'underline': '',
            'blink': '',
            'reverse video': '',
            'invisible': ''
        }
        self.fore = {
            'black': '',
            'red': '',
            'green': '',
            'yellow': '',
            'blue': '',
            'magenta': '',
            'cyan': '',
            'white': ''
        }