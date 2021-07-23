import random
import pygame
from pygameRogers import Game
from pygameRogers import Room
from pygameRogers import GameObject
from pygameRogers import TextRectangle
from pygameRogers import Alarm

# Create a new game
g = Game(1100, 600)

# Color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 77, 13)
TURQUOISE = (64, 224, 208)
RED = (255, 0, 0)

# Create Resources
titleFont = g.makeFont("Times New Roman", 128)
gameFont = g.makeFont("Arial", 38)
largerGameFont = g.makeFont("Arial", 76)
startBackground = g.makeBackground("warBG.jpg")
gameBackground = g.makeBackground(DARK_GREEN)

diamondPics = []
for i in range(2, 15):
    diamondPics.append(g.makeSpriteImage("cards\DIAMONDS" + str(i) + ".jpg"))
heartPics = []
for i in range(2, 15):
    heartPics.append(g.makeSpriteImage("cards\HEARTS" + str(i) + ".jpg"))
spadePics = []
for i in range(2, 15):
    spadePics.append(g.makeSpriteImage("cards\SPADES" + str(i) + ".jpg"))
clubPics = []
for i in range(2, 15):
    clubPics.append(g.makeSpriteImage("cards\CLUBS" + str(i) + ".jpg"))
topCard = g.makeSpriteImage("cards\TOP.jpg")

# Create Rooms
r1 = Room("Start Menu", startBackground)
g.addRoom(r1)

r2 = Room("Game", gameBackground)
g.addRoom(r2)

# Classes for Game Objects
class StartButton(TextRectangle):

	def __init__(self, text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor):
		TextRectangle.__init__(self, text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)

	def update(self):
		self.checkMousePressedOnMe(event)
		if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
			g.nextRoom()
			self.mouseHasPressedOnMe = False

class Card(GameObject):
    	
	def __init__(self, picture, value, suit):
		GameObject.__init__(self, picture)
		self.value = value
		self.suit = suit
		self.cardImage = picture	# Used when image needs to change back to card after being changed to top card during war

class PlayerDeck(GameObject):
    	
	def __init__(self, picture, xPos, yPos, hand):
		GameObject.__init__(self, picture)
		self.rect.x = xPos
		self.rect.y = yPos
		self.hand = []
		for i in hand:
			self.hand.append(i)
		self.inPlay = False		# Ensures no double-playing a card while cards are in play

	def update(self):
		self.checkMousePressedOnMe(event)

		if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
    		# Cards are only playable if cards aren't already 'inPlay' AND the game isn't over (BackupPile.gameOver = False)
			if not self.inPlay and not BackupPile.gameOver:
			# When player deck is clicked on, top card is played and cards are 'inPlay'
				self.inPlay = True
				self.playCard(self.hand[0])
			self.mouseHasPressedOnMe = False

	def playCard(self, card):
    	# Played card removed from player hand and taken by PlayedPile
		self.hand.remove(card)
		played.takeCard(card, False)
		# Timer for computer to play card is set
		cpu.playTimer.setAlarm(1000)

		# If no more cards in player hand, kill PlayerDeck
		if len(self.hand) == 0:
			self.kill()
			# A timer is set for restocking the player's hand only if war is not in effect (otherwise instant restock)
			if not PlayedPile.inWar:
				restockPile.timerA.setAlarm(2500)

class ComputerDeck(GameObject):
    
	def __init__(self, picture, xPos, yPos, hand):
		GameObject.__init__(self, picture)
		self.rect.x = xPos
		self.rect.y = yPos
		self.hand = []
		for i in hand:
			self.hand.append(i)
		self.playTimer = Alarm()

	def update(self):
    	# Timer for computer to play card is finished. Computer plays its top card
		if self.playTimer.finished():
			self.playCard(self.hand[0])

	def playCard(self, card):
    	# Played card removed from computer hand and taken by PlayedPile
		self.hand.remove(card)
		played.takeCard(card, True)

		# If no more cards in computer hand, kill ComputerDeck
		if len(self.hand) == 0:
			self.kill()
    		# A timer is set for restocking the computer's hand only if war is not in effect (otherwise instant restock)
			if not PlayedPile.inWar:
				restockPile.timerB.setAlarm(2000)

class PlayedPile(GameObject):
    	
	inWar = False
	warPrompt = TextRectangle("WAR!", 700, 450, largerGameFont, RED)

	def __init__(self, xPos, yPos):
		GameObject.__init__(self)
		self.xPos = xPos
		self.yPos = yPos
		self.playedCards = []
		self.timer = Alarm()
		self.warTimer = Alarm()

	def takeCard(self, card, cpuTurn):
		self.playedCards.append(card)
		# If PlayedPile is taking cards from player, add card to left side
		if not cpuTurn:
			card.rect.x = self.xPos - (card.rect.width / 2) * (len(self.playedCards) // 2)	# xPos changes depending on number of cards in play (for war)
			card.rect.y = self.yPos
			r2.addObject(card)
			playerCounter.setText("Player Cards Left: " + str(len(restockPile.playerPile) + len(player.hand)))
		# If PlayedPile is taking cards from computer, add card to right side
		else:
			card.rect.x = self.xPos + card.rect.width + 4 + (card.rect.width / 2) * (len(self.playedCards) / 2 - 1)	# xPos changes depending on number of cards in play (for war)
			card.rect.y = self.yPos
			r2.addObject(card)
			cpuCounter.setText("Computer Cards Left: " + str(len(restockPile.cpuPile) + len(cpu.hand)))

			# If war is not in effect, check who won the current play
			if not PlayedPile.inWar:
				self.checkWin()

		# If war is in effect, played cards have the image of the top card
		if PlayedPile.inWar:
			card.image = topCard
		
	def checkWin(self):
    	# If player wins, set 'self.playerWin' to True (paramater for restock pile's take function), then set a timer that calls a function that determines which correct restock pile to send the cards to
		if self.playedCards[-2].value > self.playedCards[-1].value:
			self.playerWin = True
			self.timer.setAlarm(1000)
	    # If computer wins, set 'self.playerWin' to False (parameter for restock pile's take function), then set a timer that calls a function that determines which correct restock pile to send the cards to
		elif self.playedCards[-2].value < self.playedCards[-1].value:
			self.playerWin = False
			self.timer.setAlarm(1000)
		# If it's a tie, war function is called
		else:
			self.war()

	def war(self):
    	# Prompt for war is diplayed. Timer is set that will play all the cards required during war
		r2.addObject(PlayedPile.warPrompt)
		self.warTimer.setAlarm(1000)

	def update(self):
    	# Alarm set by checkWin function
		if self.timer.finished():
    		# Restock pile takes cards and takes player win or loss as parameter to determine correct pile to send cards
			restockPile.takeCards(self.playerWin)
			# Cards are no longer 'inPlay' (player can play a card) as long as the computer isn't currently restocking
			if not len(cpu.hand) == 0:
				player.inPlay = False

		# Once warTimer alarm is finished...
		if self.warTimer.finished():
    		# Game is currently in war
			PlayedPile.inWar = True
			# War prompt killed once war actually begins (showed for 1 second)
			PlayedPile.warPrompt.kill()
			# Player and computer play cards 3 times (since 'inWar' = True, cards will appear as top card image)
			for i in range(3):
    			# Function call to check if either player or computer hand is empty. If so, immediately restock rather than setting a timer
				restockPile.immediateRestock()
    			# Play the 3 cards required in war for player and cpu (cards are never played if game is over)
				if not BackupPile.gameOver:
					player.playCard(player.hand[0])
					cpu.playCard(cpu.hand[0])
				# Originally, for a computer card to be played, a timer is set once the player plays a card
				# This timer is turned off and the computer plays a card instantly during war
				cpu.playTimer.alarm = False
			# Once the player and computer each play 3 cards, war is no longer in effect
			PlayedPile.inWar = False
			# Function call to check if either player or computer hand is empty. If so, immediately restock rather than setting a timer
			restockPile.immediateRestock()
			# Player and computer play 1 more card which will determine who wins all the cards in play
			# Cards are never played if game is over
			if not BackupPile.gameOver:
				player.playCard(player.hand[0])

class BackupPile(GameObject):
    
	gameOver = False
    	
	def __init__(self, xPos, yPos):
		GameObject.__init__(self)
		self.startingX = xPos
		self.startingY = yPos
		self.playerPile = []
		self.cpuPile = []
		# Timer for player restock
		self.timerA = Alarm()
		# Timer for computer restock
		self.timerB = Alarm()
		self.quitTimer = Alarm()

	def update(self):
    	# If the timer for player restock has finished, player restock is invoked
		if self.timerA.finished():
			self.restock(True)
		# If the timer for computer restock has finished, computer restock is invoked
		if self.timerB.finished():
			self.restock(False)
		# Game over; timer to quit game
		if self.quitTimer.finished():
			g.stop()

	def takeCards(self, playerWin):
    	# If war has happened, some card images will be the top card image, so they're changed back current play is over
		for c in played.playedCards:
			c.image = c.cardImage
		# If the player was won the current play...
		if playerWin:
    		# Cards in play are killed and sent to a restock list for the player
			for c in played.playedCards:
				c.kill()
				self.playerPile.append(c)
			# Last card in playedCards list appears as the top card for the player's restock pile
			played.playedCards[-1].rect.x = self.startingX
			played.playedCards[-1].rect.y = self.startingY
		# If the computer has won the current play...
		else:
    		# Cards in play are killed and sent to a restock list for the computer
			for c in played.playedCards:
				c.kill()
				self.cpuPile.append(c)
			# Last card in playedCards list appears as the top card for the computer's restock pile
			played.playedCards[-1].rect.x = self.startingX + 340
			played.playedCards[-1].rect.y = self.startingY - 400
		r2.addObject(played.playedCards[-1])
		played.playedCards.clear()
		
		# Card counters are updated after each win/loss
		playerCounter.setText("Player Cards Left: " + str(len(self.playerPile) + len(player.hand)))
		cpuCounter.setText("Computer Cards Left: " + str(len(self.cpuPile) + len(cpu.hand)))

	def immediateRestock(self):
        # Restock timers are turned off in the event a player is restocking immediately before war occurs
		self.timerA.alarm = False
		self.timerB.alarm = False
		if len(player.hand) == 0:
			self.restock(True)
		if len(cpu.hand) == 0:
			self.restock(False)

	def restock(self, playerRestock):
    	# If there are no more cards in the player hand
		if playerRestock:
    		# If there are no cards in the restock pile, player has run out of cards and loses (gameOver = True, cards can no longer be played)
			if len(self.playerPile) == 0:
				BackupPile.gameOver = True
			# Game over check prevents an error from being thrown (player can't restock without any cards left)
			if not BackupPile.gameOver:
				# Player restock pile cards shuffled
				random.shuffle(self.playerPile)
				# player object reinitialized (after being killed when running out of cards) with the cards from the restock pile
				global player
				player = PlayerDeck(topCard, 520, 450, self.playerPile)
				r2.addObject(player)
				# Cards in player restock pile killed
				for c in self.playerPile:
					c.kill()
				self.playerPile.clear()
			# Player is out of cards in restock pile and hand; game over
			elif BackupPile.gameOver:
				lose = TextRectangle("You Lose!", 420, 260, largerGameFont, TURQUOISE)
				r2.addObject(lose)
				self.quitTimer.setAlarm(3000)
		# If there are no more cards in the computer hand...
		else:
    		# If there are no cards in the restock pile, computer has run out of cards and loses
			if len(self.cpuPile) == 0:
				BackupPile.gameOver = True
			# Game over check prevents an error from being thrown (computer can't restock without any cards left)
			if not BackupPile.gameOver:
				# Computer restock pile cards shuffled
				random.shuffle(self.cpuPile)
				# cpu object reinitialized (after being killed when running out of cards) with the cards from the restock pile
				global cpu
				cpu = ComputerDeck(topCard, 520, 50, self.cpuPile)
				r2.addObject(cpu)
				# Cards in computer restock pile killed
				for c in self.cpuPile:
					c.kill()
				self.cpuPile.clear()
				# Player can play cards again only after cpu has restocked and cards are no longer in play
				if len(played.playedCards) == 0:
					player.inPlay = False
			# Player is out of cards in restock pile and hand; game over
			elif BackupPile.gameOver:
				win = TextRectangle("You Win!", 420, 260, largerGameFont, TURQUOISE)
				r2.addObject(win)
				self.quitTimer.setAlarm(3000)

# Initialize Objects in the Room
title = TextRectangle("WAR", 370, 25, titleFont, WHITE)
r1.addObject(title)

start = StartButton("START", 470, 300, gameFont, RED, 105, 40, BLACK)
r1.addObject(start)

fullDeck = []
for i in range(len(diamondPics)):
    c = Card(diamondPics[i], i + 2, "D")
    fullDeck.append(c)
for i in range(len(heartPics)):
    c = Card(heartPics[i], i + 2, "H")
    fullDeck.append(c)
for i in range(len(spadePics)):
    c = Card(spadePics[i], i + 2, "S")
    fullDeck.append(c)
for i in range(len(clubPics)):
	c = Card(clubPics[i], i + 2, "C")
	fullDeck.append(c)

random.shuffle(fullDeck)

player = PlayerDeck(topCard, 520, 450, fullDeck[:26])
r2.addObject(player)

cpu = ComputerDeck(topCard, 520, 50, fullDeck[26:])
r2.addObject(cpu)

played = PlayedPile(480, 265)
r2.addObject(played)

restockPile = BackupPile(350, 450)
r2.addObject(restockPile)

playerCounter = TextRectangle("Player Cards Left: " + str(len(restockPile.playerPile) + len(player.hand)), 20, 470, gameFont, WHITE)
r2.addObject(playerCounter)

cpuCounter = TextRectangle("Computer Cards Left: " + str(len(restockPile.cpuPile) + len(cpu.hand)), 20, 70, gameFont, WHITE)
r2.addObject(cpuCounter)

# Game Loop
g.start()

while g.running:

	# Limit the game execution framerate
	dt = g.clock.tick(60)

	# Check for Events
	for event in pygame.event.get():

		# Quit if user clicks[x]
		if event.type == pygame.QUIT:
			g.stop()

	# Update the gamestate of all the objects
	g.currentRoom().updateObjects()

	# Render the background to the window surface
	g.currentRoom().renderBackground(g)

	# Render the object images to the background
	g.currentRoom().renderObjects(g)

	# Draw everything on the screen
	pygame.display.flip()

pygame.quit()