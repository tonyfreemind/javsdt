class Person:
    def __init__(self, name, age):
        self.myName = name
        self.myAge = age

    def Introudce( self ):
        print( "My Name is ", self.myName )
    

class TonyFamily( Person ):
    def __init__(self, name, age, sing, dance ):
        Person.__init__( self, name, age )        
        self.canSing = sing
        self.canDance = dance

    def Sing( self ):
        if self.canSing:
            print( "Tony Is singing Mid night small mid song ......." )
        else:
            print( "Tony says I don't know how to sing ......." )

    def Dance( self ):
        if self.canDance:
            print( "Tony Is moonwalking ......." )
        else:
            print( "Tony says I can't dance ......." )

class Melanie( TonyFamily ):
    def __init__(self ):
        TonyFamily.__init__( self, "Melanie", 16, True, True  )        
    
        
    def Sing( self ):
        if self.canSing:
            print( "Melanie Is singing What's up Dog ......." )
        else:
            print( "Melanie says I don't know how to sing ......." )

    def Dance( self ):
        if self.canDance:
            print( "Melanie Is HipHopping ......." )
        else:
            print( "Melanie says I can't dance ......." )

class Angela( TonyFamily ):
    def __init__(self ):
        TonyFamily.__init__( self, "Angela", 9, False, False  )        
        
    def Sing( self ):
        if self.canSing:
            print( "Angela Is singing Mid night small mid song ......." )
        else:
            print( "Angela says I don't know how to sing ......." )

    def Dance( self ):
        if self.canDance:
            print( "Angela Is ShitDancing ......." )
        else:
            print( "Angela says I can't dance ......." )

p = TonyFamily( "Tony Lam", 50, True, True )
p.Sing();

p = Melanie( )
p.Sing();

p = Angela()
p.Sing()

p.Dance()