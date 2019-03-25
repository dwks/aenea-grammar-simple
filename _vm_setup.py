# commands for controlling various programs

from aenea import *

def copyGrammars():
    import os
    os.system("copy C:\\grammar\\*.py C:\\Natlink\\Natlink\\MacroSystem");
    print "Done copying, reloading grammar..."

    from _aenea import reload_code
    reload_code()

class VMSetupRule(MappingRule):
    mapping = {
        "copy in new grammars": Function(copyGrammars)
    }

grammar = dragonfly.Grammar('vm_setup')

grammar.add_rule(VMSetupRule())

grammar.load()


# Unload function which will be called at unload time.
def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
