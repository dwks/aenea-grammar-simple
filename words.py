# module for dictating words and basic sentences
#
# (based on the multiedit module from dragonfly-modules project)
# (heavily modified)
# (the original copyright notice is reproduced below)
#
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

try:
    from aenea import (Key, Text, Mimic, CompoundRule, Dictation, Pause)
except:
    from dragonfly import (Key, Text, Mimic, CompoundRule, Dictation, Pause)
import tformat

lastFormatRuleLength = 0
lastFormatRuleWords = []
def handle_word(text):
    words = str(text).split()
    print 'word (', words, ')'
    if len(words) > 0:
        Text(words[0]).execute()

        global lastFormatRuleWords
        global lastFormatRuleLength
        lastFormatRuleWords = words[0:1]
        lastFormatRuleLength = len(words[0])

        if len(words) > 1:
            Mimic(' '.join(words[1:])).execute()


class NopeFormatRule(CompoundRule):
    spec = ('nope')

    def value(self, node):
        global lastFormatRuleLength
        print "erasing previous format of length", lastFormatRuleLength
        return Key('backspace:' + str(lastFormatRuleLength))

class ReFormatRule(CompoundRule):
    spec = ('that was [upper | natural] ( proper | camel | rel-path | abs-path | score | sentence | '
            'scope-resolve | jumble | dotword | dashword | natword | snakeword | brooding-narrative)')

    def value(self, node):
        global lastFormatRuleWords
        words = lastFormatRuleWords
        words = node.words()[2:] + lastFormatRuleWords
        print words

        uppercase = words[0] == 'upper'
        lowercase = words[0] != 'natural'

        if lowercase:
            words = [word.lower() for word in words]
        if uppercase:
            words = [word.upper() for word in words]

        words = [word.split('\\', 1)[0].replace('-', '') for word in words]
        if words[0].lower() in ('upper', 'natural'):
            del words[0]

        function = getattr(tformat, 'format_%s' % words[0].lower())
        formatted = function(words[1:])

        global lastFormatRuleLength
        lastFormatRuleLength = len(formatted)
        return Text(formatted)

class FormatRule(CompoundRule):
    spec = ('[upper | natural] ( proper | camel | rel-path | abs-path | score | sentence | '
            'scope-resolve | jumble | dotword | dashword | natword | snakeword | brooding-narrative) [<dictation>] [bomb]')
    extras = [Dictation(name='dictation')]
    exported = False

    def value(self, node):
        words = node.words()
        print "format rule:", words

        uppercase = words[0] == 'upper'
        lowercase = words[0] != 'natural'

        if lowercase:
            words = [word.lower() for word in words]
        if uppercase:
            words = [word.upper() for word in words]

        words = [word.split('\\', 1)[0].replace('-', '') for word in words]
        if words[0].lower() in ('upper', 'natural'):
            del words[0]

        bomb = None
        if 'bomb' in words:
            bomb_point = words.index('bomb')
            if bomb_point+1 < len(words):
                bomb = words[bomb_point+1 : ]
            words = words[ : bomb_point]

        function = getattr(tformat, 'format_%s' % words[0].lower())
        formatted = function(words[1:])
        global lastFormatRuleWords
        lastFormatRuleWords = words[1:]

        global lastFormatRuleLength
        lastFormatRuleLength = len(formatted)

        # empty formatted causes problems here
        print "  ->", formatted
        if bomb != None:
            return Text(formatted) + Mimic(' '.join(bomb))
        else:
            return Text(formatted)

class PhraseFormatRule(CompoundRule):
    spec = ('[start] [new] phrase [<dictation>]')
    extras = [Dictation(name='dictation')]

    def value(self, node):
        words = node.words()
        print "format rule:", words

        leading = (words[0] != 'start')
        trailing = False #(words[0] != 'end' and words[0] != 'isolated')
        if words[0] == 'start' or words[0] == 'isolated': words = words[1:]
        capitalize = (words[0] == 'new')
        if words[0] == 'new': words = words[1:]
        words = words[1:]  # delete "phrase"

        if len(words) == 0: return Pause("0")

        formatted = ''
        addedWords = False
        for word in words:
            special = word.split('\\', 1)
            if(len(special) > 1 and special[1] != 'pronoun' and special[1] != 'determiner'):
                formatted += special[0]
            else:
                if(addedWords): formatted += ' '
                formatted += special[0]
                addedWords = True
        if capitalize: formatted = formatted[:1].capitalize() + formatted[1:]
        if leading: formatted = ' ' + formatted
        if trailing: formatted += ' '

        global lastFormatRuleWords
        lastFormatRuleWords = words

        global lastFormatRuleLength
        lastFormatRuleLength = len(formatted)

        print "  ->", formatted
        return Text(formatted)

