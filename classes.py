import pygame
from random import randint, random
from math import sin, cos, radians

LARGURA = 1460
ALTURA = 700
GRAVIDADE = 1.8
velocidade_cenario = 12


class Jogador(pygame.sprite.Sprite):
	def __init__(self, x, y, *grupos):
		"""--> Constrói um objeto Jogador.
		Parâmetros:
			x (int | float): a posição x do jogador;
			y (int | float): a posição y inicial do jogador;
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o jogador vai ser armazenado.
		"""
		
		super().__init__(*grupos)
		
		self.img_original = pygame.Surface((65, 65), pygame.SRCALPHA)
		
		self.modo_jogo = 'quadrado'
		if self.modo_jogo == 'quadrado':
			self.img_original.fill((100, 255, 0))
			pygame.draw.rect(self.img_original, 'black', ((0, 0), (65, 65)), 2)
		self.image = self.img_original
		self.rect = self.image.get_rect()
		self.rect.topleft = (x * 65, y * 65)
		self.vel = pygame.Vector2()
		self.mult_gravidade = 1
		self.pule = False
		self.morreu = False
		self.venceu = False
		self.angulo = 0
		self.vel_rotacao = -8
	
	def pular(self):
		"""--> Verifica se o jogador pode pular; se sim, aplica uma velocidade para cima nele."""
		
		match self.modo_jogo:
			case 'quadrado':
				if self.pule:
					self.vel.y = -24.5 * self.mult_gravidade
			case 'nave':
				if self.mult_gravidade > 0:
					self.vel.y -= 2 if self.vel.y > -10 else 0
					self.angulo += 6 if self.angulo <= 45 else 0
				elif self.mult_gravidade < 0:
					self.vel.y += 2 if self.vel.y < 10 else 0
					self.angulo -= 6 if self.angulo >= -45 else 0
			case 'bola':
				if self.pule:
					self.rect.y -= self.mult_gravidade * GRAVIDADE
					self.mult_gravidade *= -1
	
	def entrada_colisao(self, outro):
		"""--> Série de condições que determinam como o jogador vai reagir a cada tipo de colisão."""
		
		if outro.marcador == "Espinho":
			if self.rect.colliderect(outro.ret_colisao):
				self.morreu = True
			return
		
		if outro.marcador == 'Orbe de salto amarelo':
			self.pule = True
			return
		
		if outro.marcador == 'Portal':
			if 'gravidade' in outro.tipo:
				self.mult_gravidade = -1 if 'invertida' in outro.tipo else 1
				return
			
			self.modo_jogo = outro.tipo
			return
		
		if (self.rect.top, self.rect.bottom) == (outro.rect.top, outro.rect.bottom):
			self.morreu = True
			return
		
		if pygame.Rect(
				(outro.rect.left, outro.rect.top), 
				(outro.rect.width, outro.rect.height * 0.4)
			).collidepoint(self.rect.bottomright):
			if self.modo_jogo != 'quadrado' or self.mult_gravidade > 0:
				self.vel.y = 0
				if self.modo_jogo != 'bola':
					self.vel_rotacao = 0
					if self.modo_jogo == 'quadrado':
						self.angulo = self.angulo // 90 * 90
					else:
						self.angulo = 0
				self.rect.bottom = outro.rect.top
				self.pule = True
				return
			self.morreu = True
		
		elif pygame.Rect(
				(outro.rect.left, outro.rect.top + outro.rect.height * 0.6),
				(outro.rect.width, outro.rect.height * 0.4)
			).collidepoint(self.rect.topright):
			if self.modo_jogo != 'quadrado' or self.mult_gravidade < 0:
				self.vel.y = 0
				if self.modo_jogo != 'bola':
					self.vel_rotacao = 0
					if self.modo_jogo == 'quadrado':
						self.angulo = self.angulo // 90 * 90
					else:
						self.angulo = 0
				self.rect.top = outro.rect.bottom
				self.pule = True
				return
			self.morreu = True
		
		elif pygame.Rect(
			(outro.rect.left, outro.rect.top + outro.rect.height * 0.4), 
			(outro.rect.width, outro.rect.height * 0.2)
		).colliderect(self.rect):
			self.morreu = True
	
	def update(self, **kwargs):
		"""Veja pygame.sprite.Sprite.update e pygame.sprite.Group.update."""
		
		self.vel.y += GRAVIDADE * self.mult_gravidade
		self.rect.y += self.vel.y
		
		if self.pule:
			self.vel_rotacao = 0
		else:
			self.vel_rotacao = -7.5
		
		if self.modo_jogo == 'bola':
			self.vel_rotacao = 0
		elif self.modo_jogo == 'nave':
			if self.mult_gravidade > 0:
				self.vel_rotacao = -3 if self.angulo >= -45 else 0
			elif self.mult_gravidade < 0:
				self.vel_rotacao = 3 if self.angulo <= 45 else 0
		
		colisores = [
			sprite for sprite in kwargs['colisores']
			if abs(sprite.rect.center[0] - self.rect.center[0]) < 500
		]
		
		for colisor in colisores:
			if isinstance(colisor, ParedeFim) and colisor.rect.x <= self.rect.right:
				self.venceu = True
		
		colisores = pygame.sprite.spritecollide(self, kwargs['colisores'], False)
		if not colisores:
			self.pule = False
		
		for colisor in colisores:
			self.entrada_colisao(colisor)
		
		if self.rect.top not in range(-ALTURA, ALTURA):
			self.morreu = True
		
		self.angulo += self.vel_rotacao
		self.image = pygame.transform.rotate(self.img_original, self.angulo)
		self.rect = self.image.get_rect(center=self.rect.center)
		ret_img = self.img_original.get_rect()
		
		match self.modo_jogo:
			case 'quadrado':
				self.mult_gravidade = self.mult_gravidade / abs(
					self.mult_gravidade
				)
				
				self.img_original = pygame.Surface((65, 65), pygame.SRCALPHA)
				pygame.draw.rect(
					self.img_original, (100, 255, 0), ((0, 0), ret_img.size)
				)
				pygame.draw.rect(
					self.img_original, 'black', ((0, 0), ret_img.size), 2
				)
			case 'nave':
				self.mult_gravidade = 0.5 * self.mult_gravidade / abs(
					self.mult_gravidade
				)
				
				self.img_original = pygame.Surface((65, 65), pygame.SRCALPHA)
				ret_nave = pygame.Rect(
					(0, 0), (ret_img.width * 0.6, ret_img.height * 0.8)
				)
				ret_nave.center = ret_img.center
				
				pygame.draw.rect(self.img_original, (100, 255, 0), ret_nave)
				pygame.draw.polygon(self.img_original, (100, 255, 0), [
					ret_nave.topright, (ret_img.right, ret_nave.centery - 15), 
					(ret_img.right, ret_nave.centery + 15), ret_nave.bottomright
				])
				pygame.draw.polygon(self.img_original, (100, 255, 0), [
					ret_nave.topleft, (ret_img.left, ret_nave.top - 15), 
					(ret_img.left, ret_nave.bottom + 15), ret_nave.bottomleft
				])
				
				pygame.draw.polygon(self.img_original, 'black', [
					(ret_img.left, ret_nave.top - 15), ret_nave.topleft,
					ret_nave.topright, (ret_img.right, ret_nave.centery - 15), 
					(ret_img.right, ret_nave.centery + 15), ret_nave.bottomright,
					ret_nave.bottomleft, (ret_img.left, ret_nave.bottom + 15)
				], 2)
				
			case 'bola':
				self.mult_gravidade = 0.5 * self.mult_gravidade / abs(
					self.mult_gravidade
				)
				
				self.img_original = pygame.Surface((65, 65), pygame.SRCALPHA)
				pygame.draw.circle(
					self.img_original, (100, 255, 0),
					ret_img.center, 32.5
				)
				pygame.draw.circle(
					self.img_original, 'black', 
					ret_img.center, 32.5, 2
				)
			case _:
				raise Exception('Modo de jogo inválido!')


class Chao(pygame.sprite.Sprite):
	marcador = 'Chao'
	
	def __init__(self, x, y, cor, *grupos):
		"""--> Constrói um objeto Chao.
		
		Parâmetros:
			x (int | float): a posição x do ladrilho do chão;
			y (int | float): a posição y do ladrilho do chão;
			cor (tuple[int] | pygame.Color | ColorValue)
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o ladrilho vai ser armazenado.
		"""
		
		super().__init__(*grupos)
		
		self.image = pygame.Surface((LARGURA // 5, ALTURA / 4))
		self.image.fill(cor)
		pygame.draw.rect(
			self.image, 'white', ((0, 0), (LARGURA // 5, ALTURA / 4)), 2
		)
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y * 65)
	
	def update(self, **kwargs):
		"""Veja pygame.sprite.Sprite.update e pygame.sprite.Group.update."""
		
		self.rect.x -= velocidade_cenario
		if self.rect.right <= 0:
			self.rect.x = LARGURA


class Bloco(pygame.sprite.Sprite):
	marcador = 'Bloco'
	
	def __init__(self, x, y, *grupos):
		"""--> Constrói um objeto Bloco.
		
		Parâmetros:
			x (int | float): a posição x do bloco;
			y (int | float): a posição y do bloco;
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o bloco vai ser armazenado.
		"""
		
		super().__init__(*grupos)
		
		imagem = pygame.Surface((65, 65))
		pygame.draw.rect(
			imagem, (255, 255, 255), ((0, 0), (65, 65)), 2
		)
		self.image = imagem
		self.rect = self.image.get_rect(topleft=(x * 65, y * 65))
	
	def update(self, **kwargs):
		"""Veja pygame.sprite.Sprite.update e pygame.sprite.Group.update."""
		
		self.rect.x -= velocidade_cenario


class BlocoDecor(Bloco):
	marcador = 'Bloco de Decoração'
	
	def __init__(self, x, y, *grupos):
		"""--> Constrói um objeto BlocoDecor, que herda de Bloco.
		
		Parâmetros:
			x (int | float): a posição x do bloco;
			y (int | float): a posição y do bloco;
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o bloco vai ser armazenado.
		"""
		
		super().__init__(x, y, *grupos)
		
		self.image.fill((0, 0, 100, 50))


class Espinho(pygame.sprite.Sprite):
	marcador = 'Espinho'
	altura = 65
	desloc = pygame.Vector2(65 / 3, altura / 2)

	def __init__(self, x, y, angulo, *grupos):
		"""--> Constrói um objeto Espinho.
		
		Parâmetros:
			x (int | float): a posição x do espinho;
			y (int | float): a posição y do espinho;
			angulo (int | float): o ângulo de rotação anti-horária do espinho em graus (valores negativos para rotação no sentido horário). O ângulo fornecido é arredondado para o seu menor e mais próximo múltiplo de 90.
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o espinho vai ser armazenado.
		"""
		
		super().__init__(*grupos)
		
		self.angulo = angulo // 90 * 90

		self.img_original = pygame.Surface((65, self.altura), pygame.SRCALPHA).convert_alpha()
		self.rect = self.img_original.get_rect()
		self.img_original.fill((0, 0, 0, 0))
		
		pygame.draw.polygon(
			self.img_original, 'black', [
				(self.rect.left, self.rect.bottom),
				(self.rect.centerx, self.rect.top),
				(self.rect.right, self.rect.bottom)
			]
		)
		pygame.draw.polygon(
			self.img_original, 'white', [
				(self.rect.left, self.rect.bottom),
				(self.rect.centerx, self.rect.top),
				(self.rect.right, self.rect.bottom)
			], 2
		)
		
		self.image = pygame.transform.rotate(self.img_original, self.angulo)
		
		self.rect.topleft = (x * 65, y * 65)

		if self.angulo % 360 == 0 or self.angulo % 180 == 0:
			self.ret_colisao = pygame.Rect(
				(0, 0), (self.desloc.x, self.desloc.y)
			)
		
			self.ret_colisao.center = (
				self.rect.centerx, 
				self.rect.bottom - self.rect.height / 4 if self.angulo % 360 == 0 else self.rect.top + self.rect.height / 4
			)
		else:
			self.ret_colisao = pygame.Rect(
				(0, 0), (self.desloc.y, self.desloc.x)
			)
			
			self.ret_colisao.center = (
				self.rect.left + self.rect.width / 4 if self.angulo % 270 == 0 else self.rect.right - self.rect.width / 4, 
				self.rect.centery
			)

	def update(self, **kwargs):
		"""Veja pygame.sprite.Sprite.update e pygame.sprite.Group.update."""
		
		self.rect.x -= velocidade_cenario
		self.ret_colisao.x -= velocidade_cenario
		
		self.image = pygame.transform.rotate(self.img_original, self.angulo)


class MeioEspinho(Espinho):
	altura = 32.5
	
	def __init__(self, x, y, angulo, *grupos):
		"""--> Constrói um objeto MeioEspinho, que herda de Espinho.
		
		Parâmetros:
			x (int | float): a posição x do espinho;
			y (int | float): a posição y do espinho;
			angulo (int | float): o ângulo de rotação anti-horária do espinho em graus. O ângulo é arredondado para o menor e mais próximo múltiplo de 90 do ângulo fornecido.
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o espinho vai ser armazenado.
		"""
		
		super().__init__(x, y, angulo, *grupos)
		
		self.rect.y += self.altura


class OrbeSaltoAmarelo(pygame.sprite.Sprite):
	marcador = 'Orbe de salto amarelo'
	
	def __init__(self, x, y, *grupos):
		"""--> Constrói um objeto OrbeSaltoAmarelo.
		
		Parâmetros:
			x (int | float): a posição x do orbe;
			y (int | float): a posição y do orbe;
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o orbe vai ser armazenado.
		"""
		
		super().__init__(*grupos)
		
		imagem = pygame.Surface((65, 65), pygame.SRCALPHA)
		self.rect = imagem.get_rect()
		pygame.draw.circle(imagem, 'yellow', self.rect.center, 17)
		pygame.draw.circle(imagem, 'white', self.rect.center, 32, 2)
		self.image = imagem
		
		self.rect.topleft = (x * 65, y * 65)
	
	def update(self, **kwargs):
		"""Veja pygame.sprite.Sprite.update e pygame.sprite.Group.update."""
		
		self.rect.x -= velocidade_cenario


class Portal(pygame.sprite.Sprite):
	marcador = 'Portal'
	
	def __init__(self, x, y, tipo, *grupos):
		"""--> Constrói um objeto Portal.
		
		Parâmetros:
			x (int | float): a posição x inicial do portal;
			y (int | float): a posição y inicial do portal;
			tipo (str): o tipo do portal. O portal pode ter um de 5 tipos: 'quadrado', 'nave', 'bola', 'gravidade invertida' e 'gravidade normal'.
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde o portal vai ser armazenado.
		"""
		
		super().__init__(*grupos)
		
		self.tipo = tipo.strip().casefold()
		self.image = pygame.Surface((50, 130), pygame.SRCALPHA)
		self.rect = self.image.get_rect()
		
		cor = (0, 0, 0)
		match self.tipo:
			case 'quadrado':
				cor = (0, 255, 0)
			case 'nave':
				cor = (255, 0, 255)
			case 'bola':
				cor = (255, 100, 0)
			case 'gravidade invertida':
				cor = (255, 255, 0)
			case 'gravidade normal':
				cor = (0, 255, 255)
			case _:
				cor = (0, 0, 0)
		
		self.image.fill(cor)
		pygame.draw.rect(self.image, 'black', (
			(self.rect.left + 10, self.rect.top), (self.rect.width - 20, self.rect.height)
		))
		pygame.draw.rect(self.image, 'white', self.rect, 2)
		
		self.rect.topleft = (x * 65, y * 65)
	
	def update(self, **kwargs):
		self.rect.x -= velocidade_cenario


class ParedeFim(pygame.sprite.Sprite):
	marcador = 'Parede do fim'
	largura, altura = 65 * 1, 65 * 8 # largura: 65 * 14
	
	def __init__(self, grupo_colisores, *grupos_principais):
		"""--> Constrói um objeto ParedeFim.
		
		Parâmetros:
			x (int | float): a posição x da parede final;
			y (int | float): a posição y da parede final;
			grupos (tuple[pygame.sprite.Group]): tupla de argumentos posicionais para se referir aos grupos onde a parede final vai ser armazenada.
		"""
		
		super().__init__(*grupos_principais)
		
		self.image = pygame.Surface(
			(self.largura, self.altura), 
			pygame.SRCALPHA
		)
		pygame.draw.rect(
			self.image, (0, 0, 100), ((0, 0), (self.largura, self.altura))
		)
		pygame.draw.rect(
			self.image, 'white', ((0, 0), (self.largura, self.altura)), 2
		)
		self.rect = self.image.get_rect()
		
		pontos_acerto = list()

		for raio in range(0, self.altura * 65, 65):
			sprite_projetil = RaioProjetil(21.6, raio + 32.5)
			cond_acerto = lambda: (
				(colisor := pygame.sprite.spritecollideany(
					sprite_projetil, grupo_colisores
				)) and colisor.marcador != self
			)
			pontos_acerto.append(
				sprite_projetil.lancar(
					20, pygame.Vector2(1, 0), 65, cond_acerto
				).x - 21.6
			)
		
		self.rect.x = max(pontos_acerto) + 65
		
		self.emissor = Emissor(self.rect.x, 0, altura=self.altura)

	def update(self, **kwargs):
		"""Veja pygame.sprite.Sprite.update e pygame.sprite.Group.update."""
		
		self.rect.x -= velocidade_cenario
		
		self.emissor.emitir(
			1, pygame.Vector2(-1, 0), 3, (170, 220, 255), 
			False, kwargs['particulas']
		)
		self.emissor.verificar()


class Emissor:
	def __init__(
		self, x, y, largura_ou_raio=0, altura=0
	):
		"""--> Constrói um objeto Emissor.
		
		Parâmetros:
			x (int | float): a posição x inicial do emissor;
			y (int | float): a posição y do emissor;
			largura_ou_raio (int | float): a largura ou raio do emissor;
			altura (int | float): a altura do emissor.
		"""
		
		self.pos = pygame.Vector2(x, y)
		self.largura = self.raio = largura_ou_raio
		self.altura = altura
		
		self._lista_particulas = list()
	
	def emitir(
		self, quantidade, direcao, velocidade_max, cor, radial=False, *grupos
	):
		"""--> Emite certa quantidade de partículas, em uma certa direção, em uma determinada velocidade máxima, com uma certa cor, de uma determinada forma, armazenadas em certos grupos.
		
		Parâmetros:
			quantidade (int): a quantidade de objetos Particula a serem instanciados;
			direcao (pygame.Vector2): a direção normalizada para a qual as partículas viajarão;
			velocidade_max (int | float): a velocidade máxima com que as partículas viajarão;
			cor (tuple[int] | pygame.Color | ColorValue): a cor das partículas geradas;
			radial (bool): indica se a emissão de partículas é radial (de forma circular);
			grupos: uma tupla que contém os grupos onde serão inseridas as partículas.
		"""
		
		if self.pos.x in range(0, LARGURA) and self.pos.y in range(0, ALTURA):
			for _ in range(quantidade):
				pos = pygame.Vector2()
				if radial:
					pos_relativa = pygame.Vector2(
						cos(radians(randint(0, 360))) * randint(-self.raio, self.raio),
						sin(radians(randint(0, 360))) * randint(-self.raio, self.raio)
					)
					pos = self.pos + pos_relativa
				else:
					pos.x = randint(int(self.pos.x), int(self.pos.x) + self.largura)
					pos.y = randint(int(self.pos.y), int(self.pos.y) + self.altura)
				nova_particula = Particula(
					*pos.xy, direcao, velocidade_max, cor, radial, *grupos
				)
				self._lista_particulas.append(nova_particula)
	
	def verificar(self):
		"""--> Atualiza a própria instância e verifica o estado das partículas, matando-as se o seu tempo de vida se esgotar."""
	
		self.pos.x -= velocidade_cenario
		novas_particulas = []
	
		for particula in self._lista_particulas:
			if particula.tempo_vida <= 0:
				particula.kill()
			else:
				novas_particulas.append(particula)
		
		self._lista_particulas = novas_particulas

class Particula(pygame.sprite.Sprite):
	def __init__(self, x, y, direcao, velocidade_max, cor, radial, *grupos):
		"""--> Constrói um objeto Particula.
		
		Parâmetros:
			x (int | float): a posição x inicial da partícula;
			y (int | float): a posição y inicial da partícula;
			direcao (pygame.Vector2): a direção normalizada do movimento da partícula;
			velocidade_max (int): a velocidade máxima com que a partícula viajará;
			cor (tuple[int] | pygame.Color | ColorValue): a cor da partícula;
			radial (bool): indica se a partícula será emitida de forma radial (de forma circular);
			grupos (tuple[pygame.sprite.Group]): uma tupla que contém os grupos onde a partícula será inserida.
		"""
		
		super().__init__(*grupos)
		self.image = pygame.Surface((8, 8))
		self.image.fill(cor)
		self.rect = self.image.get_rect(center=(x, y))
		
		self.vel = pygame.Vector2()
		if radial:
			x = random() * 2 - 1
			y = random() * 2 - 1
			while x == 0 == y:
				y = random() * 2 - 1
				x = random() * 2 - 1
			vetor_aux = pygame.Vector2(x, y)
			self.vel = vetor_aux.normalize() * randint(1, velocidade_max)
		else:
			self.vel = direcao * randint(1, velocidade_max)
		
		self.tempo_vida = 150

	def update(self):
		"""Veja pygame.sprite.Sprite.update e pygame.sprite.Group.update."""
		
		self.rect.x += self.vel.x - velocidade_cenario
		self.rect.y += self.vel.y
		if self.tempo_vida > 0:
			self.tempo_vida -= 5
		
		self.image.set_alpha(self.tempo_vida)


class RaioProjetil:
	"""^ Classe que representa um raio lançável. ^"""
	
	def __init__(self, x, y):
		"""--> Constrói um objeto RaioProjetil.
		
		Parâmetros:
			x (int | float): a posição x inicial do raio;
			y (int | float): a posição y do raio.
		"""
			
		self.rect = pygame.Rect((x, y), (10, 10))
		
	def lancar(self, dist_max, direcao, incr, cond_acerto):
		"""--> Lança o objeto em uma direção, retornando seu ponto de parada.
		
		Parâmetros:
			dist_max (int | float): a distância até onde o raio irá;
			direcao (pygame.Vector2): a direção normalizada para onde o raio irá;
			incr (int | float): o incremento para o deslocamento do raio;
			cond_acerto (function -> bool): a condição de acerto do raio (o objeto irá parar ao último atendimento da condição).
			
		Retorna: o ponto (pygame.Vector2) de chegada do raio.
		"""
		
		dist_percorrida = 0
		delta_dist = pygame.Vector2(direcao.x * incr, direcao.y * incr)
		ponto = pygame.Vector2()
		
		while True:
			dist_percorrida += 1
			acertou = cond_acerto()
			self.rect.x += delta_dist.x
			self.rect.y += delta_dist.y
			
			if acertou:
				ponto.xy = self.rect.x, self.rect.y
				dist_percorrida = 0
			
			if dist_percorrida > dist_max:
				break
			
		return ponto


def ajuda(documentado):
	raise Exception(documentado.__doc__)


objetos_estaticos = (
	Bloco, BlocoDecor, Espinho, MeioEspinho, 
	OrbeSaltoAmarelo, Portal
)
