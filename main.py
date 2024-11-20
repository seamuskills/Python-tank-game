import pygame, random

pygame.init()
sc = pygame.display.set_mode((512,256),pygame.FULLSCREEN)
c = pygame.time.Clock()
font = pygame.font.SysFont(None,24)

#die image
dieIcon = pygame.image.load("die.png")
dieIcon = pygame.transform.scale(dieIcon,(16,16))
GearImg = pygame.image.load("gear.png")
GearImg = pygame.transform.scale(GearImg,(16,16))

#score list (player1,player2)
score = [0,0]
maxhp = 3

#explanation of low damage numbers
print("players have 3 hp, splash damage does around 0.5 max and a \ndirect hit does 1 damage. you cannot die from splash damage.\n goodluck!")

#get length in direction
def move_toward(pos1,pos2):
	pos1 = pygame.Vector2(pos1)
	pos2 = pygame.Vector2(pos2)
	return pygame.Vector2(pos1-pos2).normalize()

#get distance between pos1 and pos2
def dist(pos1,pos2):
	x1 = pos1[0]
	x2 = pos2[0]
	y1 = pos1[1]
	y2 = pos2[1]
	return ((x2-x1)**2+(y2-y1)**2)**0.5

#sprite groups
tanks = pygame.sprite.Group()
bullets = pygame.sprite.Group()

terrain = None
terrainsurf = pygame.surface.Surface((512,256)) #surface

def defaultTerrain():
	global terrainsurf
	global terrain
	#terrain
	terrainsurf.fill((255,255,255)) #fill white
	pygame.draw.polygon(terrainsurf,(255,100,0),[(0,128),(25,130),(40,140),(80,160),(120,170),(256,180),(512-120,170),(512-80,160),(512-40,140),(512-25,130),(512,128),(512,256),(0,256)]) #create terrain polygon using points
	terrainsurf.set_colorkey((255,255,255)) #set white as transparent
	terrain = pygame.mask.from_surface(terrainsurf) #get mask

defaultTerrain()

bgsurf = pygame.surface.Surface((512,256))
bgsurf.fill((100,100,255))
 #reset terrainsurf
polygon = [[0,128],[25,130],[40,140],[80,160],[120,170],[256,180],[512-120,170],[512-80,160],[512-40,140],[512-25,130],[512,128],[512,256],[0,256]] #get the polygon again but with lists instead of tuples
for i in polygon:
	i[1] += -20+random.randint(-20,20) #shufle the points around
pygame.draw.polygon(bgsurf,(200,200,200),polygon)

def randomize():
	global terrain
	global terrainsurf
	terrainsurf.fill((255,255,255)) #reset terrainsurf
	polygon = [[0,128],[25,130],[40,140],[80,160],[120,170],[256,180],[512-120,170],[512-80,160],[512-40,140],[512-25,130],[512,128],[512,256],[0,256]] #get the polygon again but with lists instead of tuples
	for i in polygon:
		i[1] += random.randint(-20,20) #shufle the points around
	pygame.draw.polygon(terrainsurf,(255,100,0),polygon) #draw it to the surface
	terrainsurf.set_colorkey((255,255,255)) #make white transparent
	terrain = pygame.mask.from_surface(terrainsurf) #get mask

#circle mask (player size)
circle = pygame.surface.Surface((16,16))
circle.fill((255,255,255))
circle.set_colorkey((255,255,255))
pygame.draw.circle(circle,(0,0,0),(8,8),8)
circleMask = pygame.mask.from_surface(circle)

#circle mask (bullet size)
SmallCircle = pygame.surface.Surface((8,8))
SmallCircle.fill((255,255,255))
SmallCircle.set_colorkey((255,255,255))
pygame.draw.circle(SmallCircle,(0,0,0),(4,4),4)
SmallCircleMask = pygame.mask.from_surface(circle)

#circle mask (bullet impact size)
bigCircle = pygame.surface.Surface((32,32))
bigCircle.fill((255,255,255))
bigCircle.set_colorkey((255,255,255))
pygame.draw.circle(bigCircle,(0,0,0),(16,16),16)
bigCircleMask = pygame.mask.from_surface(bigCircle)

grav = 0.05 #gravity
turn = 0 #who's turn it is

class tank(pygame.sprite.Sprite): #tank
	def __init__(self,x,y,player):
		super().__init__(tanks) #init as sprite in tanks group
		self.image = pygame.Surface((16,16))
		pygame.draw.circle(self.image,(255,255,255),(8,8),8)
		self.image.set_colorkey((0,0,0)) #set black as transparent
		self.rect = [x,y,16,16] #set up collision rect
		self.player = player #what turn this tank moves on
		self.move = 16 #how much longer this tank can move
		self.power = 1 #how much power this tank shoots a shot with
		self.point = (-10,-10) #last point fired at
		self.hp = maxhp #health
	
	def update(self):
		global turn
		target = pygame.mouse.get_pos() #get mouse position
		keys = pygame.key.get_pressed() #keys pressed
		if keys[pygame.K_d] == True and self.move > 0: #move right
			self.rect[0] += 0.2*dt
			self.move -= 1
		if keys[pygame.K_a] == True and self.move > 0: #move left
			self.rect[0] -= 0.2*dt
			self.move -= 1
		if keys[pygame.K_w]: #power up
			self.power += 0.01
		if keys[pygame.K_s]: #power down
			self.power -= 0.01
		self.power = max(0,min(self.power,1.5))
		if firing: #space held?
			projectile(self.rect[0],self.rect[1],target,self.power,self.player) #spawn projectile
			self.point = target #set the point last aimed
			turn = int(not turn) #reset turn
			self.move = 16 #reset movement

		pygame.draw.rect(sc,(255,255,0),(self.rect[0]-8,self.rect[1]-12,(self.power/1.5)*32,4)) #draw power bar
		pygame.draw.rect(sc,(0,255,0),(self.rect[0]-8,self.rect[1]-8,(self.move/16)*32,4)) #draw move bar
		pygame.draw.rect(sc,(255,0,0),(self.rect[0]-8,self.rect[1]-4,(self.hp/maxhp)*32,4)) #draw hp bar
		self.rect[0] = max(16,min(self.rect[0],512-16)) #keep x within the map
		iterations = 0 #iterations of going down
		while terrain.overlap(circleMask,(int(self.rect[0]),int(self.rect[1]+1))) == None: #check if above terrain
			self.rect[1] += 1 #move down
			iterations += 1 
			if iterations > 128: #failsafe
				raise SystemError("you fell somehow!") #idiot
		while terrain.overlap(circleMask,(int(self.rect[0]),int(self.rect[1]))) != None: #check if inside terrain
			self.rect[1] -= 1 #move up

		pygame.draw.circle(sc,(255,0,0),(self.point[0]-2,self.point[1]+2),4) #draw the point last aimed

def reset():
	global tank0
	global tank1
	tanks.empty() #reset tanks
	tank0 = tank(10,128-16,0)
	tank1 = tank(512-26,128-16,1)

class projectile(pygame.sprite.Sprite): #bullet
	def __init__(self,x,y,target,power,owner):
		super().__init__(bullets) #sprite init
		self.rect = [x,y,4,4] #rect for collisions
		self.image = pygame.Surface((8,8)) #graphic of self
		self.image.fill((255,255,255)) #fill w/ white
		pygame.draw.circle(self.image,(0,0,0),(4,4),4)
		self.image.set_colorkey((255,255,255)) #white is transparent
		self.hsp,self.vsp = move_toward((self.rect[0],self.rect[1]),target) #set horizontal/vertical speed
		self.hsp *= (3*power)
		self.vsp *= (3*power)
		self.owner = owner #set owner

	def update(self):
		global bigCircleMask
		global SmallCircleMask
		global grav
		self.rect[0] -= (self.hsp*dt)/7.5 #move x
		self.rect[1] -= (self.vsp*dt)/7.5 #move y
		self.vsp -= grav #use gravity
		for i in tanks: #loop through tanks
			if pygame.Rect(self.rect).colliderect(i.rect): #collision with tank?
				if i.player != self.owner: #is enemy tank?
					i.hp -= 1 #reduce hp
					if i.hp <= 0: #if player ded
						print("player "+str(int(self.owner)+1)+" won")
						#exit()
						global tank0
						global tank1
						score[self.owner] += 1 #do scoring
						print("p1, p2\n"+str(score))
						reset()
					print("direct hit! 1 damage!")
					self.owner = i.player #don't hurt the enemy anymore by becoming the enemy bullet
					self.hsp = 0 #get rid of speed
					self.vsp = -1
		if terrain.overlap(SmallCircleMask,(int(self.rect[0]),int(self.rect[1]))): #check if terrain hit
			terrain.erase(bigCircleMask,(int(self.rect[0]),int(self.rect[1]))) #make indent
			otherTank = eval("tank"+str(int(not self.owner)))
			damage = max(0,(24-(dist(self.rect,otherTank.rect)))*0.037) #splash damage
			otherTank.hp -= damage #subtract damage
			if damage > 0: print("splash damage: "+str(damage))
			bullets.remove(self)

class die: #randomization die
	def __init__(self):
		self.x = 512-33
		self.y = 0
		self.w,self.h = 16, 16
	
	def update(self):
		sc.blit(dieIcon,(self.x,self.y))
		if pygame.mouse.get_pressed(3)[0] == True and pygame.Rect(self.x,self.y,self.w,self.h).collidepoint(pygame.mouse.get_pos()): #if click randomize terrain.
			randomize()

def hpup():
	global maxhp
	maxhp += 0.05

def hpdown():
	global maxhp
	maxhp -= 0.05

class Gear:
	def __init__(self):
		self.x = 512-16
		self.y = 0 
		self.w,self.h = 16,16
		self.active = False #menu open
		self.options = {"Settings:":None,"reset map":defaultTerrain,"randomize map":randomize,"reset tanks":reset,"/\ ":hpup,"tank max hp":None,"\/":hpdown} #list of options and function that tie to them
		self.variables = {"tank max hp: ":"round(maxhp,2)","p1 hp: ":"round(tank0.hp,2)","p2 hp: ":"round(tank1.hp,2)","p1 movement:":"round(tank0.move,2)","p2 movement":"round(tank1.move,2)","p1 power: ":"round(tank0.power,2)","p2 power: ":"round(tank1.power,2)"} #list of variables to display
		self.pressedprev = False

	def update(self):
		if self.active: #if open
			surf = pygame.Surface((200,250)) #make a surface
			surf.fill(pygame.Color(100,100,100)) #fill it
			surf.set_alpha(128) #set its opacity
			sc.blit(surf,(6,3)) #draw it to the screen
			string = [i for i in self.options.keys()]
			for i in string:
				text = font.render(i,True,(255,255,255))
				size = font.size(i) ##get size of current text
				rect = pygame.Rect(12,6+size[1]*1.1*string.index(i),size[0],size[1])
				pygame.draw.rect(sc,(34,34,34),rect) ##debug
				sc.blit(text,(12,6+string.index(i)*size[1]*1.1))
				if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed(3)[0] == True: ##if mouse over an pressed
					if (self.options[i] != None):
						self.options[i]()
			sc.blit(surf,(306,3))
			for k,v in self.variables.items():
				v = eval(v)
				text = font.render(k+str(v),True,(255,255,255))
				size = font.size(k+str(v))
				rect = pygame.Rect(312,6+size[1]*1.1*list(self.variables.keys()).index(k),size[0],size[1])
				pygame.draw.rect(sc,(34,34,34),rect)
				sc.blit(text,(312,6+list(self.variables.keys()).index(k)*size[1]*1.1))

		sc.blit(GearImg,(self.x,self.y))
		if pygame.mouse.get_pressed(3)[0] == True and pygame.Rect(self.x,self.y,self.w,self.h).collidepoint(pygame.mouse.get_pos()) and self.pressedprev == False: #if click randomize terrain.
			self.active = not self.active
			self.pressedprev = True
		else:
			if not pygame.mouse.get_pressed(3)[0]:
				self.pressedprev = False

tank0 = tank(10,128-16,0)
tank1 = tank(512-26,128-16,1)

firing = False

Die = die()

settings = Gear()

dt = 0
while True:
	firing = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				firing = True

	sc.blit(bgsurf,(0,0))

	Die.update()

	terrainsurf = terrain.to_surface()
	terrainsurf.set_colorkey((0,0,0))
	sc.blit(terrainsurf,(0,0))

	eval("tank"+str(turn)+".update()")
	tanks.draw(sc)

	bullets.update()
	bullets.draw(sc)
	settings.update()

	fpstext = font.render(str(round(c.get_fps(),2)),True,(0,0,0))
	sc.blit(fpstext,(0,0))

	pygame.display.flip()
	dt = c.tick(60)