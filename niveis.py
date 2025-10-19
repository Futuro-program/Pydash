import pygame
if __name__ != '__main__':
	import Niveis.classes as objs_jogo
from typing import ABCMeta, abstractmethod


class Nivel(metaclass=ABCMeta):
	nome = 'Nível genérico'
	musica = ''
	pos_musica = 0
	cor_fundo = 'blue'
	
	def _inicializacao(self, **grupos):
		for v in grupos.values():
			v.empty()
			
		jogador = objs_jogo.Jogador(8, 7, grupos['desenho'])
		
		for x in range(0, objs_jogo.LARGURA + 1, objs_jogo.LARGURA // 5):
			chao = objs_jogo.Chao(
				x, 8, self.cor_fundo, grupos['desenho'], grupos['colisores']
			)
		
		return jogador
	
	@abstractmethod
	def level_design(self, **grupos):
		raise NotImplementedError('Implemente a inicialização!')
	
	def _inicializacao_final(self, **grupos):
		parede_final = objs_jogo.ParedeFim(
			grupos['colisores'],
			grupos['desenho'],
			grupos['colisores']
		)
			
		botao_pausar = pygame.Rect((objs_jogo.LARGURA - 100, 100), (50, 50))
		botao_sair = pygame.Rect((objs_jogo.LARGURA - 200, 100), (50, 50))
		botoes = (botao_pausar, botao_sair)
			
		relogio = pygame.time.Clock()
		TQPS  = 60
			
		fonte_debug = pygame.font.SysFont('arial', 32)
		
		rodando = True
		
		return (
			botao_pausar, botao_sair, botoes, relogio, 
			TQPS, fonte_debug, rodando
		)

	def _loop(
		self, tela, jogador, botao_pausar, botao_sair, botoes, relogio, 
		TQPS, fonte_debug, lista_pause=None, **grupos
	):
		if lista_pause is None:
			lista_pause = [False]
		
		pausado = lista_pause[0]
		
		for evento in pygame.event.get():
			if evento.type == pygame.QUIT:
				rodando = False
			if evento.type == pygame.MOUSEBUTTONDOWN:
				if botao_pausar.collidepoint(evento.pos):
					pausado = not pausado
						
				if pausado and botao_sair.collidepoint(evento.pos):
					return True
				
		if not pausado:
			pygame.mixer.music.unpause()
					
			if pygame.mouse.get_pressed()[0]:
				jogador.pular()
					
			grupos['desenho'].update(
				colisores=grupos['colisores'],
				 particulas=grupos['particulas']
			 )
			grupos['particulas'].update()
		else:
			pygame.mixer.music.pause()
				
		if jogador.morreu:
			particulas_morte = objs_jogo.Emissor(*jogador.rect.center, 130)
			particulas_morte.emitir(
				35, pygame.Vector2(-1, 0), 7, (170, 220, 255), 
				True, grupos['particulas']
			)
			
			particulas_morte.verificar()
			
		if jogador.venceu:
			return True
			
		tela.fill(self.cor_fundo)
		grupos['desenho'].draw(tela)
		grupos['particulas'].draw(tela)
				
		if pausado:
			pygame.draw.rect(
				tela, pygame.Color(100, 100, 100, 0), 
				((0, 0), (objs_jogo.LARGURA, objs_jogo.ALTURA))
			)
		
		for botao in botoes:
			if botao == botao_sair and not pausado:
				continue
			pygame.draw.rect(tela, (255, 255, 0), botao, border_radius=5)
				
		pygame.draw.line(
			tela, (0, 255, 0), (botao_pausar.left + 20, botao_pausar.top + 10), 
			(botao_pausar.left + 20, botao_pausar.bottom - 10), 5
		)
		pygame.draw.line(
			tela, (0, 255, 0), (botao_pausar.right - 20, botao_pausar.top + 10), 
			(botao_pausar.right - 20, botao_pausar.bottom - 10), 5
		)
				
		if pausado:
			pygame.draw.line(
				tela, (0, 255, 0), (botao_sair.left + 10, botao_sair.top + 10), 
				(botao_sair.right - 10, botao_sair.bottom - 10), 5
			)
			pygame.draw.line(
				tela, (0, 255, 0), (botao_sair.right - 10, botao_sair.top + 10), 
				(botao_sair.left + 10, botao_sair.bottom - 10), 5
			)
				
		for sprite in grupos['desenho'].sprites():
			if sprite.rect.right < 0 and sprite.__class__ in objs_jogo.objetos_estaticos:
				sprite.kill()
				
		texto_debug = fonte_debug.render(
			f'Gamemode{jogador.modo_jogo}', True, 'red'
		)
		tela.blit(texto_debug, texto_debug.get_rect())
				
		pygame.display.flip()
		relogio.tick(TQPS)
		
		lista_pause[0] = pausado

	def rodar(self, tela, **grupos):
		jogador = self._inicializacao(**grupos)
		self.level_design(**grupos)
		(
			botao_pausar, botao_sair, botoes, relogio, 
			TQPS, fonte_debug, rodando
		) = self._inicializacao_final(**grupos)
		
		pygame.mixer.music.play()
		pygame.mixer.music.set_pos(self.pos_musica)
		
		lista_pause = [False]
		
		while rodando:
			if jogador.morreu or self._loop(
				tela, jogador, botao_pausar, botao_sair, botoes, relogio, 
				TQPS, fonte_debug, lista_pause, **grupos
			):
				rodando = False
		
		if jogador.venceu:
			pygame.mixer.music.fadeout(500)
		else:
			pygame.mixer.music.stop()
		pygame.mixer.music.unload()
		return not jogador.morreu


class Nivel1(Nivel):
	nome = 'Let\'s Go!'
	musica = 'Mídia/Lensko - Let\'s Go! [NCS Release].mp3'
	pos_musica = 47
	cor_fundo = (20, 100, 255)
	
	_lista_inst = [None]
	
	def __new__(cls):
		if not cls._lista_inst[0]:
			cls._lista_inst[0] = super().__new__(cls)
		
		return cls._lista_inst[0]
	
	def level_design(self, **grupos):
		portal = objs_jogo.Portal(
			18, 4.5, 'quadrado', grupos['desenho'], grupos['colisores']
		)
		portal = objs_jogo.Portal(
			25, 4.5, 'gravidade normal', grupos['desenho'], grupos['colisores']
		)
	
		for x in range(15, 868):
			bloco = objs_jogo.Bloco(x, 7, grupos['desenho'], grupos['colisores'])
		
		pygame.mixer.music.load(self.musica)


class Nivel2(Nivel):
	nome = 'Dancefloor Dreamer'
	musica = 'Mídia/NIVIRO - Dancefloor Dreamer [NCS Release].mp3'
	pos_musica = 1.7
	cor_fundo = (255, 20, 100)
	
	_lista_inst = [None]
	
	def __new__(cls):
		if not cls._lista_inst[0]:
			cls._lista_inst[0] = super().__new__(cls)
		
		return cls._lista_inst[0]
	
	def level_design(self, **grupos):
		portal = objs_jogo.Portal(
			15, 5.5, 'bola', grupos['desenho'], grupos['colisores']
		)

		for x in range(15, 60):
			bloco = objs_jogo.Bloco(x, 5, grupos['desenho'], grupos['colisores'])
			espinho = objs_jogo.Espinho(
				x, 4, 0, grupos['desenho'], grupos['colisores']
			)
	
		pygame.mixer.music.load(self.musica)


class Nivel3(Nivel):
	nome = 'Polaris'
	musica = 'Mídia/Blazars - Polaris [NCS Release].mp3'
	pos_musica = 46
	cor_fundo = (20, 100, 50)
	
	_lista_inst = [None]
	
	def __new__(cls):
		if not cls._lista_inst[0]:
			cls._lista_inst[0] = super().__new__(cls)
		
		return cls._lista_inst[0]
	
	def level_design(self, **grupos):
		portal = objs_jogo.Portal(
			15, 5.5, 'nave', grupos['desenho'], grupos['colisores']
		)
	
		portal = objs_jogo.Portal(
			20, 5.5, 'gravidade invertida', grupos['desenho'], grupos['colisores']
		)
		
		for x in range(16, 60):
			bloco = objs_jogo.Bloco(x, 3, grupos['desenho'], grupos['colisores'])
	
		pygame.mixer.music.load(self.musica)


def selecao_niveis(num_nivel):
	"""--> Retorna o num_nivel-ésimo nível de todos_niveis.
	
	Parâmetro: num_nivel (int): o número do nível selecionado, representado por um número natural não nulo.
	"""
	return todos_niveis[num_nivel - 1]


nivel1 = Nivel1()
nivel2 = Nivel2()
nivel3 = Nivel3()

todos_niveis = (nivel1, nivel2, nivel3)
