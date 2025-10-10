import pygame
import Niveis.classes as objs_jogo
from Niveis import niveis
from random import randint

pygame.init()

LARGURA = objs_jogo.LARGURA
ALTURA = objs_jogo.ALTURA
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.SRCALPHA)
pygame.display.set_caption('Pydash')

grupo_desenho = pygame.sprite.Group()
grupo_colisores = pygame.sprite.Group()
grupo_particulas = pygame.sprite.Group()

cor_fundo = (randint(50, 255), randint(50, 255), randint(50, 255))

botao_inicio = pygame.Rect((0, 0), (170, 170))
botao_inicio.center = (LARGURA / 2, ALTURA / 2)
botao_anterior = pygame.Rect((0, 0), (100, 100))
botao_anterior.center = (100, ALTURA / 2)
botao_proximo = pygame.Rect((0, 0), (100, 100))
botao_proximo.center = (LARGURA - 100, ALTURA / 2)
botao_sair = pygame.Rect((0, 0), (50, 50))
botao_sair.center = (LARGURA - 100, 100)
botoes = (botao_inicio, botao_anterior, botao_proximo, botao_sair)

relogio = pygame.time.Clock()
TQPS  = 60

fonte_titulo = pygame.font.SysFont('arial', 64, bold=True)

rodando = True
num_nivel = 1
while rodando:
	for evento in pygame.event.get():
		if evento.type == pygame.QUIT:
			rodando = False
		
		elif evento.type == pygame.MOUSEBUTTONDOWN:
			if botao_inicio.collidepoint(evento.pos):
				rodando_nivel = True
				while rodando_nivel:
					for evento in pygame.event.get():
						if evento.type == pygame.QUIT:
							rodando_nivel = False
					
					nivel_selecionado = niveis.selecao_niveis(num_nivel)
					if nivel_selecionado(
							tela, desenho=grupo_desenho,
						 	colisores=grupo_colisores, particulas=grupo_particulas
						):
						rodando_nivel = False
			
			elif botao_anterior.collidepoint(evento.pos):
				num_nivel -= 1
				if num_nivel < 1:
					num_nivel = len(niveis.todos_niveis)
			
			elif botao_proximo.collidepoint(evento.pos):
				num_nivel += 1
				if num_nivel > len(niveis.todos_niveis):
					num_nivel = 1
			
			elif botao_sair.collidepoint(evento.pos):
				rodando = False
	
	tela.fill(cor_fundo)
	
	indicador_nivel = fonte_titulo.render(
		f'Nível {num_nivel}', True, 
		(255 - cor_fundo[0], 255 - cor_fundo[1], 255 - cor_fundo[2])
	)
	ret_indicador_nivel = indicador_nivel.get_rect()
	ret_indicador_nivel.center = (LARGURA / 2, 100)
	
	for botao in botoes:
		pygame.draw.rect(tela, (255, 255, 0), botao, border_radius=10)
	
	pygame.draw.polygon(tela, (0, 255, 0), [
		(700, 320), (760, 350), (700, 380)
	])
	
	pygame.draw.polygon(tela, (0, 255, 0), [
		(botao_anterior.centerx + 15, botao_anterior.top + 10), 
		botao_anterior.center, 
		(botao_anterior.centerx + 15, botao_anterior.bottom - 10), 
		(botao_anterior.left + 20, botao_anterior.centery)
	])
	pygame.draw.polygon(tela, (0, 255, 0), [
		(botao_proximo.centerx - 15, botao_proximo.top + 10), 
		botao_proximo.center, 
		(botao_proximo.centerx - 15, botao_proximo.bottom - 10), 
		(botao_proximo.right - 20, botao_proximo.centery)
	])
	
	pygame.draw.line(
		tela, (0, 255, 0), (botao_sair.left + 10, botao_sair.top + 10), 
		(botao_sair.right - 10, botao_sair.bottom - 10), 5
	)
	pygame.draw.line(
		tela, (0, 255, 0), (botao_sair.right - 10, botao_sair.top + 10), 
		(botao_sair.left + 10, botao_sair.bottom - 10), 5
	)
	
	tela.blit(indicador_nivel, ret_indicador_nivel)

	pygame.display.flip()
	relogio.tick(TQPS)
			
pygame.quit()
