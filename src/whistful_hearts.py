class Card():
    '''Class regarding card objects.'''

    def __init__(self, card):
        '''Accepts length 2 strings as the argument.'''
        # Suit and pip value of a card respectively.
        self.suit = card[1]
        self.pip = str(card[0] if card[0] not in '0JQKA' else '0JQKA'.index(card[0]) + 10)

        # Checks whether a card is a Heart or the Queen of Spades.
        self.isHearts = True if self.suit == 'H' else False
        self.isQueenSpades = True if self.suit == 'S' and self.pip == '12' else False


class Trick():
    '''Class for trick objects. 'curr_trick', 'prev_tricks' and 'deck_top'
    are passed to this class.'''

    def __init__(self, trick):
        '''Accepts tuples or lists as the argument.'''
        # Whether player is the leader for the current trick,
        # whether game is in the preliminary or scoring rounds,
        # and filters the 10 scoring rounds.
        self.isLead = True if len(trick) == 0 else False
        self.isRounds10 = True if len(trick) > 2 else False
        self.Rounds10 = trick[3:] if self.isRounds10 else []

        # Determines trump and lead of trick respectively,
        # and whether trick contains Hearts.
        self.trump = (Card(trick[0]).suit if type(trick[0]) == str else Card(trick[0][0]).suit) if not self.isLead else None
        self.lead = Card(trick[0]).suit if not self.isLead else None
        self.hasHearts = True if len([card for card in trick if Card(card).isHearts]) > 0 else False


class Hand():
    '''Class of the 'hand' of a player.'''

    def __init__(self, hand, trump=False, lead=False, suit=False):
        '''Accepts list as argument, with optional trump, lead and/or
        specific suit to check for.'''
        # Checks condition of hand if having leads or not, if hand
        # contains the Queen of Spades or if hand is full of hearts.
        self.noLead = True if lead and len([card for card in hand if lead in card]) == 0 else False
        self.hasLead = True if lead and len([card for card in hand if lead in card]) > 0 else False
        self.hasQueenSpades = True if True in [True for card in hand if Card(card).isQueenSpades] else False
        self.allHearts = True if sum([1 if Card(card).isHearts else 0 for card in hand], 0) == len(hand) else False

        # Checks for the highest and lowest card in hand respectively.
        self.highest = '234567890JQKA'[max([(int(Card(card).pip), Card(card).suit) for card in hand])[0] - 2] + max([(int(Card(card).pip), Card(card).suit) for card in hand])[1] if len(hand) > 0 and not suit else False
        self.lowest = '234567890JQKA'[min([(int(Card(card).pip), Card(card).suit) for card in hand])[0] - 2] + min([(int(Card(card).pip), Card(card).suit) for card in hand])[1] if len(hand) > 0 and not suit else False

        # Sublists containing all trumps, leads, hearts, and other suits.
        self.trumps = [card for card in hand if trump in card] if trump else []
        self.leads = [card for card in hand if lead in card] if lead else []
        self.hearts = [card for card in hand if Card(card).isHearts]
        self.others = [card for card in hand if card not in self.trumps and card not in self.leads]

        # Counts hand for the number of cards of suit respective to
        # that defined in argument 'suit'.
        self.count = sum([1 if suit in card else 0 for card in hand], 0) if suit else False


class Score():
    '''Class relating to calculating scores of players in a game.'''

    def __init__(self, tricks, deck_top):
        '''Accepts a list of tricks and overturned cards as arguments.'''
        # Initialises default score, ordering of players, and counter
        # for shooting the moon.
        self.score = [0, 0, 0, 0]
        self.order = [0, 1, 2, 3]
        self.moon = 0

        # Iterates over each trick, appending scores respective to
        # the ordering of players in a particular trick, starting
        # with the winner of the last trick.
        for trick in tricks:
            self.order = Player(self.order, trick, deck_top, tricks.index(trick)).order
            self.score[self.order[0]] += Player(self.order, trick, deck_top, tricks.index(trick)).score
            self.moon += Player(self.order, trick, deck_top, tricks.index(trick)).moon

        # Determines whether a player has shot the moon, in which case
        # all point-bearing cards have been played and all but one player
        # has 0 points as scores.
        self.shoot = True if self.moon == 14 and self.score.count(0) == 3 else False


class Player():
    '''Class considering aspects of entities playing the game.'''

    def __init__(self, order, trick, deck, index):
        '''Accepts player ordering, 'curr_trick', 'deck_top' and
        the current round ID.'''

        # Filters trick for cards prioritising trumps > leads > rest.
        self.contenders = [card for card in trick if Trick(trick).lead in card] if index > 2 else [card for card in trick if Trick(deck).trump in card] if len([card for card in trick if Trick(deck).trump in card]) != 0 else [card for card in trick if Trick(trick).lead in card]

        # Determines the winning and losing card respectively.
        self.winner = trick.index('234567890JQKA'[max([int(Card(card).pip) for card in self.contenders]) - 2] + [Card(card).suit for card in self.contenders][0])
        self.loser = trick.index('234567890JQKA'[min([int(Card(card).pip) for card in self.contenders]) - 2] + [Card(card).suit for card in self.contenders][0])

        # Switches order of players for use in the next round.
        self.order = [order[self.winner], order[self.winner + 1 if self.winner + 1 < 4 else self.winner - 3], order[self.winner + 2 if self.winner + 2 < 4 else self.winner - 2], order[self.winner + 3 if self.winner + 3 < 4 else self.winner - 1]]

        # Determines the winner's score and point relating to shooting
        # the moon for a given round based on Hearts and Queen of Spades.
        self.score = sum([1 if Card(card).isHearts else 13 if Card(card).isQueenSpades else 0 for card in trick], 0) if index > 2 else 0
        self.moon = sum([1 for card in trick if Card(card).isHearts or Card(card).isQueenSpades], 0)


class Data():
    '''Class pertaining to everything related to a given round in the
    game, to be used and passed on as player_data subsequently. If not
    specifying the trump and lead, class calculates data relating to the
    start of a trick. Else, class determines valid cards to be played'''

    def __init__(self, hand, curr=False, prev=False, deck=False, trump=False, lead=False, index=False):
        '''Accepts a 'hand', optionally arguments for 'curr_trick',
        'prev_tricks', 'deck_top', trump, lead and index of round.'''
        # Case where index is specified. (Determining
        # specific sets of cards to play).
        if index:
            # Initialises index, trump and lead (Index
            # passed as 1 higher to avoid 0 being False).
            self.index = index - 1
            self.trump = trump
            self.lead = lead

            # Filters hand for cards pertaining to trumps,
            # leads, hearts and the remainder.
            self.trumps = Hand(hand, trump=self.trump).trumps
            self.leads = Hand(hand, lead=self.lead).leads
            self.hearts = Hand(hand, trump=self.trump, lead=self.lead).hearts
            self.others = Hand(hand, trump=self.trump, lead=self.lead).others

            # Cases regarding the 3 preliminary rounds.
            if self.index <= 3:
                # Initialises the highest and lowest card corresponding
                # to their specified suits.
                self.bigTrumps = Hand(self.trumps).highest
                self.smallTrumps = Hand(self.trumps).lowest
                self.bigLeads = Hand(self.leads).highest
                self.smallLeads = Hand(self.leads).lowest
                self.bigHearts = Hand(self.hearts).highest
                self.smallHearts = Hand(self.hearts).lowest
                self.bigOthers = Hand(self.others).highest
                self.smallOthers = Hand(self.others).lowest

            # Cases regarding the 10 scoring rounds.
            else:
                # Initialises the highest and lowest card corresponding
                # to their specified suits.
                self.bigLeads = Hand(self.leads).highest
                self.smallLeads = Hand(self.leads).lowest
                self.bigHearts = Hand(self.hearts).highest
                self.smallHearts = Hand(self.hearts).lowest
                self.bigOthers = Hand(self.others).highest
                self.smallOthers = Hand(self.others).lowest

        # Case where trump and lead is not specified (Data
        # regarding initial state of round).
        else:
            # Determines round ID and card to be won in 'deck_top'.
            self.index = len(prev) + 1 if prev else 1
            self.prize = deck[self.index - 1] if deck and self.index <= 3 else False

            # Initialises trump and lead, and checks whether
            # the player is leading the trick.
            self.trump = Trick(deck).trump if deck else False
            self.lead = Trick(curr).lead if curr else False
            self.isLead = Trick(curr).isLead if curr else False

            # Determines hand for possibility of shooting the moon.
            self.tryShoot = True if (sum([1 for card in hand if Card(card).isHearts], 0) > 4 and Hand(hand).hasQueenSpades) else False

            # Checks if hearts are broken and filters the list for all
            # valid cards to be played.
            self.brokenHearts = True if curr and prev and is_broken_hearts([] if len(prev) == 0 else prev, () if len(curr) == 0 else curr) else False
            self.validPlay = [card for card in hand if self.lead in card] if self.lead and not Trick(curr).isLead and Hand(hand, lead=self.lead).hasLead else [card for card in hand if not Card(card).isHearts] if not Hand(hand).allHearts else hand

            # Counter for each suit respectively in all arguments.
            self.countDiamonds = (Hand(hand, suit='D').count if hand else 0) + (Hand(curr, suit='D').count if curr else 0) + (Hand(prev, suit='D').count if prev else 0) + (Hand(deck, suit='D').count if deck else 0)
            self.countClubs = (Hand(hand, suit='C').count if hand else 0) + (Hand(curr, suit='C').count if curr else 0) + (Hand(prev, suit='C').count if prev else 0) + (Hand(deck, suit='C').count if deck else 0)
            self.countHearts = (Hand(hand, suit='H').count if hand else 0) + (Hand(curr, suit='H').count if curr else 0) + (Hand(prev, suit='H').count if prev else 0) + (Hand(deck, suit='H').count if deck else 0)
            self.countSpades = (Hand(hand, suit='S').count if hand else 0) + (Hand(curr, suit='S').count if curr else 0) + (Hand(prev, suit='S').count if prev else 0) + (Hand(deck, suit='S').count if deck else 0)

            # Initialises data dictionary to be passed as 'player_data'.
            self.data = {'hand': hand, 'curr': curr, 'prev': prev, 'deck': deck, 'index': self.index, 'prize': self.prize, 'trump': self.trump, 'lead': self.lead, 'isLead': self.isLead, 'tryShoot': self.tryShoot, 'brokenHearts': self.brokenHearts, 'validPlay': self.validPlay, 'countDiamonds': self.countDiamonds, 'countClubs': self.countClubs, 'countHearts': self.countHearts, 'countSpades': self.countSpades}


class Play():
    '''Class pertaining to the strategy used in the 'play' function.'''

    def __init__(self, data):
        '''Accepts a dictionary returned by 'player_data' every round.'''
        # More than one valid card to be played.
        if len(data['validPlay']) > 1:
            # 3 preliminary rounds.
            if data['index'] <= 3:
                # Attempts shooting the moon.
                if data['tryShoot']:
                    # Prioritises winning the overturned Heart.
                    if Card(data['prize']).isHearts:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'bigTrumps' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigTrumps
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            # Plays prioritising 'bigTrumps' > 'bigLeads' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigTrumps
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigLeads if not self.play else self.play
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                    # Prioritises losing for higher chance of winning later.
                    else:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'smallOthers' > 'smallTrumps'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallTrumps if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            # Plays prioritising 'smallOthers' > 'smallLeads' > 'smallTrumps'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallLeads if not self.play else self.play
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallTrumps if not self.play else self.play

                # Avoids shooting the moon.
                else:
                    # Prioritises not winning the overturned Heart.
                    if Card(data['prize']).isHearts:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'smallOthers' > 'smallTrumps'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallTrumps if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            # Plays prioritising 'smallOthers' > 'smallLeads' > 'smallTrumps'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallLeads if not self.play else self.play
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallTrumps if not self.play else self.play

                    # Prioritises winning for higher chance of losing later.
                    else:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'bigTrumps' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigTrumps
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            # Plays prioritising 'bigTrumps' > 'bigLeads' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigTrumps
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigLeads if not self.play else self.play
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

            # 10 scoring rounds.
            else:
                # Attempts shooting the moon.
                if data['tryShoot']:
                    # Prioritises winning to obtain points.
                    if data['brokenHearts']:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'bigHearts' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigHearts
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            # Plays prioritising 'bigHearts' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigHearts
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                    # Prioritises breaking Hearts and winning.
                    else:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'bigHearts' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigHearts
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            # Plays prioritising 'bigHearts' > 'bigOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigHearts
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                # Avoids shooting the moon.
                else:
                    # Prioritises losing to avoid points.
                    if data['brokenHearts']:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'smallHearts' > 'smallOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallHearts
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            if Trick(data['curr']).hasHearts:
                                # Plays prioritising 'smallHearts' > 'smallLeads' > 'smallOthers'.
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallHearts
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallLeads if not self.play else self.play
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers if not self.play else self.play

                            else:
                                # Plays prioritising 'bigHearts' > 'bigLeads' > 'bigOthers'.
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigHearts
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigLeads if not self.play else self.play
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

                    # Prioritises losing and getting rid of Hearts.
                    else:
                        # Player is leading trick.
                        if data['isLead']:
                            # Leads prioritising 'smallHearts' > 'smallOthers'.
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallHearts
                            self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers if not self.play else self.play

                        # Player is not leading trick.
                        else:
                            if Trick(data['curr']).hasHearts:
                                # Plays prioritising 'smallHearts' > 'smallLeads' > 'smallOthers'.
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallHearts
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallLeads if not self.play else self.play
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).smallOthers if not self.play else self.play

                            else:
                                # Plays prioritising 'bigHearts' > 'bigLeads' > 'bigOthers'.
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigHearts
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigLeads if not self.play else self.play
                                self.play = Data(data['validPlay'], trump=data['trump'], lead=data['lead'], index=data['index'] + 1).bigOthers if not self.play else self.play

            # Safety measure in the event above code does not work.
            if not self.play:
                self.play = data['validPlay'][0]

        # Only one valid card playable.
        else:
            self.play = data['validPlay'][0]


def is_broken_hearts(prev_tricks, curr_trick=()):
    '''Returns True if hearts have been broken in the 10 scoring rounds
    of the game, and False otherwise.'''
    # Checks for presence of Hearts in both 'prev_tricks' (after the
    # third round) and 'curr_trick' if specified.
    return(True if True in [True if Card(card).isHearts else False for card_list in Trick(prev_tricks).Rounds10 for card in card_list] or [True if Card(card).isHearts else False for card_list in Trick(prev_tricks).Rounds10 for card in curr_trick] else False)


def is_valid_play(play, curr_trick, hand, prev_tricks, broken=is_broken_hearts):
    '''Returns True if play is valid, and False otherwise.'''
    # Returns False if one of the three invalid conditions are met:
    # 1 : Card in 'play' is not in 'hand'.
    # 2 : Played a Heart when 'hand' does not consist of all Hearts,
    # hearts have not been broken, game is in the 10 scoring rounds,
    # and player is the leading the trick.
    # 3 : Played a Heart when 'hand' does not consist of all Hearts,
    # hearts have not been broken, game is in the 10 scoring rounds,
    # and player is not leading and not following the lead.
    return(True if play in hand and (False if (Trick(prev_tricks).isRounds10 and Card(play).isHearts and not broken(prev_tricks, curr_trick) and not (Hand(hand, Trick(curr_trick).lead).allHearts and Hand(hand, Trick(curr_trick).lead).noLead if Trick(curr_trick).lead else Hand(hand, Trick(curr_trick).lead).allHearts)) else True) else False)


def score_game(tricks, deck_top):
    '''Returns a 4-tuple of integers, representing the score for each
    of the four players in a game.'''
    # Negates the score of the 'chosen one' if thou has shot the moon,
    # and returns the score of players in a particular game.
    # Note : Calculation is handled by both 'Player' and 'Score'
    # classes above.
    return(tuple([-number for number in Score(tricks, deck_top).score]) if Score(tricks, deck_top).shoot else tuple(Score(tricks, deck_top).score))


def play(curr_trick, hand, prev_tricks, deck_top, is_valid=is_valid_play, score=score_game, player_data=None, suppress_player_data=False):
    '''Returns a single card which represents this player's next play,
    and optionally a second argument containing an updated player_data'''
    # Returns a card as a string if player_data is suppressed, else
    # a 2-tuple containing the card and 'player_data'.
    # Note : Strategy used is determined in the 'Play' class above.
    # Note : 'player_data' is handled by the 'Data' class above.
    return(Play(Data(hand, curr=curr_trick, prev=prev_tricks, deck=deck_top).data).play if suppress_player_data else (Play(Data(hand, curr=curr_trick, prev=prev_tricks, deck=deck_top).data).play, Data(hand, curr_trick, prev_tricks, deck_top).data))


def predict_score(hand):
    '''Returns an integer prediction of this player's score on
    completion of the game based on the scoring system.'''
    # Note : May contain high inaccuracies.
    return(len([card for card in hand if Card(card).isHearts and int(Card(card).pip) > 7]) + (13 if len([card for card in hand if Card(card).isQueenSpades]) > 0 else 0) if sum([1 if Card(card).isHearts and Card(card).isQueenSpades else 0 for card in hand], 0) < 6 else -(len([card for card in hand if Card(card).isHearts and int(Card(card).pip) > 7]) + (13 if len([card for card in hand if Card(card).isQueenSpades]) > 0 else 0)))


def get_winner_score(trick, round_id, deck_top):
    '''Returns a 2-tuple containing the index of the winner of the trick
    relative to player ordering and score for the current trick.'''
    # For use when a 'random-game.py' file is bestowed upon us as to
    # enable us to play against ourselves *inserts Forever Alone meme*
    # while waiting for the announcement of the 'Grok Leaderboard'.
    # Note : As with 'score_game', calculation handled by 'Player' class.
    return(Player((0, 0, 0, 0), trick, deck_top, round_id - 1).winner, Player((0, 0, 0, 0), trick, deck_top, round_id - 1).score)

def main():
    is_broken_hearts([('JD', '6D', '0D', '9D')])
    is_broken_hearts([('6S', '9S', '2S', '5S'), ('KH', '6H', '0H', '9H'), ('KD', '6D', '0D', 'AD'), ('JD', '2D', '3D', 'QD'), ('7D', 'AH', '8D', '3S'), ('4S', 'JS', 'QS', '0S'), ('KC', 'AC', '4C', '7C'), ('7S', 'JC', 'KS', '8S')], ())
    is_valid_play('0D', (), ['0D', '9S', '3S', '3D', '3H', '5D', 'AD', '6C', '7D', '6H'], [])
    is_valid_play('KS', (), ['0D', '9S', '3S', '3D', '3H', '5D', 'AD', '6C', '7D', '6H', 'JH'], [])
    score_game([('AH', '2H', '9H', 'JH'), ('KS', '2S', 'AS', 'QS')], ['9S', '0H', '7D'])
    score_game([('3S', '0S', '8S', 'JS'), ('9H', 'QH', '0D', '5H'), ('AD', '8D', '2D', '3D'), ('4S', 'QS', '9S', '2S')], ['5D', '2S', '7S'])
    play(['8C'], ['KH', '7C', '2S', '6S', 'JS', '0D', '8H', '3S'], [('AC', '3C', '0C', '6C'), ('KD', '8D', '5D', '4D'), ('JH', '0H', '5H', '2H'), ('AS', 'KS', 'QS', '9S'), ('3D', '9D', 'JD', '7D')], ['JH', 'AS', '7S'], suppress_player_data=True)
    predict_score(['0D', '9S', '3S', '3D', '3H', '5D', 'AD', '6C', '7D', '6H'])
    predict_score(['0D', '9S', '3S', '3D', '3H', '5D', 'AD', '6C', '7D', '6H', 'JH'])
    predict_score(['7C', '4H'])
    predict_score(['0D', '9S', '3S', '3D', '3H', '5D', 'AD', '6C', '7D', 'JH'])
    predict_score(['JH', '3S', '2H', '9H', 'JS', '5C', '8H', 'KD', 'AD', '7H'])
    predict_score(['JS', '6H', '3D', 'QS', '6C', '4H', '9H', 'AS', 'QC', '0D'])
    predict_score(['6S', '5C', '7C', '5D', 'JD', '7D', '4D', '2C', 'QS', '9C'])
    predict_score(['8D', '6S', '8S', '5H', '0C', '7D', '3D', 'KC', '4C'])
    predict_score(['JH', '3H', '2H', '9H', '5H', '7H', '8H', '0H', 'QH', 'KH'])
    predict_score(['KH', '7C', '2S', '6S', 'JS', '0D', '8H', '3S'])
    predict_score(['7S', '5C', '9S', '7C', '4C', '7D', '6S', '3H', '9D', '0S'])
    predict_score(['KH', '3H', '6H', '2H', 'AH', '2S'])
    predict_score(['QD', 'JS', '7H', 'AS', 'AH', '4C', '8H', '3D', 'KD', 'QS'])

if __name__ == '__main__':
    main()
