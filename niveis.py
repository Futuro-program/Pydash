import pygame
import Niveis.classes as objs_jogo


def func_nivel(cor_fundo, pos_musica):
	""" --> O decorador responsável pela lógica interna dos níveis.
	
	Parâmetros do decorador:
		cor_fundo (tuple[int] | pygame.Color | ColorValue): a cor que será aplicada ao fundo e ao chão.
		pos_musica (int | float): a posição, em segundos, de onde a música começará.
		
		Parâmetros da função decorada:
			tela (pygame.Surface): onde serão mostrados os sprites e o fundo;
			grupos (dict[pygame.sprite.Group]): dicionário de argumentos de palavra-chave para referir-se ao grupo principal (desenho), ao grupo de sprites colisíveis com o jogador (colisores) e ao grupo de partículas (particulas).
		
		O layout do nível e o carregamento da música são definidos na definição da função decorada.
		
		A cada funcão de nível, adicione-a à tupla todos_niveis.
		
		É preferível colocar objetos a, no máximo, 20 unidades de distância da origem, e, no mínimo, a 5 unidades de distância.
		
		Retorna True se o usuário fechar o jogo ou se concluir a fase, retorna None se o jogador morrer.
		"""
	def main(nivel):
		def invol(tela, **grupos):
			for v in grupos.values():
				v.empty()
			
			jogador = objs_jogo.Jogador(8, 7, grupos['desenho'])
			
			for x in range(0, objs_jogo.LARGURA + 1, objs_jogo.LARGURA // 5):
				chao = objs_jogo.Chao(
					x, 8, cor_fundo, grupos['desenho'], grupos['colisores']
				)
			
			nivel(tela, **grupos)
			
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
			
			pygame.mixer.music.play()
			pygame.mixer.music.set_pos(pos_musica)
			
			fonte_debug = pygame.font.SysFont('arial', 32)
			
			rodando = True
			pausado = False
			colidiu = False
			while rodando:
				for evento in pygame.event.get():
					if evento.type == pygame.QUIT:
						rodando = False
					if evento.type == pygame.MOUSEBUTTONDOWN:
						if botao_pausar.collidepoint(evento.pos):
							pausado = not pausado
						
						if pausado and botao_sair.collidepoint(evento.pos):
							pygame.mixer.music.stop()
							pygame.mixer.music.unload()
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
					if not colidiu:
						particulas_morte.emitir(35, pygame.Vector2(-1, 0), 7, (170, 220, 255), True, grupos['particulas'])
						colidiu = True
						rodando = False
					particulas_morte.verificar()
				
				if jogador.venceu:
					pygame.mixer.music.fadeout(500)
					pygame.mixer.music.unload()
					return True
			
				tela.fill(cor_fundo)
				grupos['desenho'].draw(tela)
				grupos['particulas'].draw(tela)
				
				if pausado:
					tela.fill((100, 100, 100, 0))
				
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
			pygame.mixer.music.stop()
		return invol
	return main

@func_nivel((20, 100, 255), 46)
def nivel1(tela, **grupos):
	"""Song: Lensko - Let's Go! [NCS Release]
Music provided by NoCopyrightSounds
Free Download/Stream: http://ncs.io/letsgo
Watch: http://youtu.be/mSLuJYtl89Y"""
	bloco = objs_jogo.Bloco(15, 6, grupos['desenho'], grupos['colisores'])
	portal = objs_jogo.Portal(
		18, 4.5, 'nave', grupos['desenho'], grupos['colisores']
	)
	portal = objs_jogo.Portal(
		25, 4.5, 'quadrado', grupos['desenho'], grupos['colisores']
	)
	
	for x in range(15, 876):
		bloco = objs_jogo.Bloco(x, 7, grupos['desenho'], grupos['colisores'])
	
	
	
	pygame.mixer.music.load(f'Mídia/Lensko - Let\'s Go! [NCS Release].mp3')


@func_nivel((255, 20, 100), 1.7)
def nivel2(tela, **grupos):
	"""Song: NIVIRO - Dancefloor Dreamer
Music provided by NoCopyrightSounds
Free Download/Stream: http://ncs.io/DancefloorDreamer
Watch: http://ncs.lnk.to/DancefloorDreamerAT/youtube"""

	for x in range(15, 40):
		bloco = objs_jogo.Bloco(x, 5, grupos['desenho'], grupos['colisores'])
		espinho = objs_jogo.Espinho(
			x, 4, 0, grupos['desenho'], grupos['colisores']
		)
	
	pygame.mixer.music.load(f'Mídia/NIVIRO - Dancefloor Dreamer [NCS Release].mp3')
	

@func_nivel((20, 100, 50), 46)
def nivel3(tela, **grupos):
	"""Song: Blazars - Polaris [NCS Release]
Music provided by NoCopyrightSounds
Free Download/Stream: http://ncs.io/polaris
Watch: http://youtu.be/5FvBg_9BDkY"""
	
	portal = objs_jogo.Portal(
		15, 5.5, 'nave', grupos['desenho'], grupos['colisores']
	)
	
	portal = objs_jogo.Portal(
		20, 5.5, 'gravidade invertida', grupos['desenho'], grupos['colisores']
	)
	for x in range(16, 30):
		bloco = objs_jogo.Bloco(x, 3, grupos['desenho'], grupos['colisores'])
	
	pygame.mixer.music.load(f'Mídia/Blazars - Polaris [NCS Release].mp3')


def selecao_niveis(num_nivel):
	"""--> Retorna o num_nivel-ésimo nível de todos_niveis.
	
	Parâmetro: num_nivel (int): o número do nível selecionado, representado por um número natural não nulo.
	"""
	return todos_niveis[num_nivel - 1]


todos_niveis = (nivel1, nivel2, nivel3)
