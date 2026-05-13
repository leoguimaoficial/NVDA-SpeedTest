# NVDA SpeedTest

O **NVDA SpeedTest** permite realizar testes de velocidade da internet diretamente pelo NVDA. Ele mede download, upload, ping, jitter e perda de pacotes, apresentando os resultados em janelas acessíveis, com histórico, detalhes, diagnóstico e exportação.

## Funcionalidades

* Teste rápido com seleção automática de servidor.
* Teste avançado com escolha manual do servidor.
* Opção para lembrar um servidor favorito na tela de teste avançado.
* Resultados falados e exibidos em texto.
* Diagnóstico opcional em linguagem simples após cada teste.
* Unidades de velocidade configuráveis opcionais: Mbps, Gbps, MB/s e GB/s.
* Alertas configuráveis opcionais para download baixo, upload baixo, ping alto e perda de pacotes.
* Histórico de testes com data, resumo e servidor usado.
* Resumo do histórico com médias, melhores/piores resultados, comparação com o teste anterior, filtros por data e exportação.
* Exportação do histórico filtrado para CSV ou JSON.
* Detalhes completos de cada teste, incluindo servidor, jitter, perda de pacotes, provedor e IPs.
* Cópia de itens dos detalhes para a área de transferência com `Ctrl+C` ou o botão **Copiar item selecionado**.
* Botão para cancelar um teste em andamento.
* Atalho configurável, por padrão `NVDA+Shift+L`.

## Como usar

1. Abra o NVDA SpeedTest com `NVDA+Shift+L` ou pelo menu do NVDA em **Ferramentas > Internet Speed Test**.
2. Pressione **Iniciar teste rápido** para executar um teste normal com seleção automática de servidor.
3. Pressione **Teste avançado...** para escolher manualmente um servidor.
4. Na tela de teste avançado, marque **Lembrar este servidor da próxima vez** se quiser que ele venha selecionado ao abrir essa tela novamente.
5. Use **Cancelar** para parar um teste em andamento.
6. Selecione um item do histórico e pressione **Ver detalhes** para consultar o resultado completo.
7. Use os controles do histórico nesta ordem: **Ver detalhes**, **Excluir**, **Resumo do histórico** e **Limpar histórico**.
8. Pressione **Resumo do histórico** para ver médias, melhores/piores resultados, comparação com o teste anterior, filtros e opções de exportação.
9. Pressione **Configurações...** para ativar recursos opcionais, configurar alertas e escolher a unidade de velocidade exibida.
10. Para copiar um item dos detalhes, abra **Ver detalhes**, selecione o item e pressione `Ctrl+C` ou **Copiar item selecionado**.
11. Para alterar o atalho, vá em **Preferências > Definir comandos** e procure por **NVDA SpeedTest**.

## Configurações

A seleção avançada de servidor e o resumo do histórico vêm ativados por padrão. Diagnóstico, unidades personalizadas e alertas continuam desativados até serem habilitados em **Configurações...**. A tela inclui:

* **Ativar seleção avançada de servidor:** mostra ou oculta o botão de teste avançado e permite testar com servidor fixo.
* **Ativar resumo inteligente do histórico:** mostra ou oculta o botão de resumo do histórico.
* **Ativar diagnóstico simples após os testes:** adiciona comentários em linguagem simples depois de cada teste.
* **Ativar unidade de exibição personalizada:** permite escolher uma unidade diferente do padrão Mbps.
* **Unidade de velocidade exibida:** escolha Mbps, Gbps, MB/s ou GB/s quando unidades personalizadas estiverem ativadas.
* **Ativar alertas de conexão:** faz o NVDA avisar quando o resultado sair dos limites configurados.
* **Download mínimo (Mbps):** alerta quando o download ficar abaixo desse valor.
* **Upload mínimo (Mbps):** alerta quando o upload ficar abaixo desse valor.
* **Ping máximo (ms):** alerta quando o ping ficar acima desse valor.
* **Perda máxima de pacotes (%):** alerta quando a perda de pacotes passar desse valor.

A ordem de tabulação da tela de configurações mantém os controles relacionados juntos. Ao ativar unidades personalizadas, o próximo controle é a escolha de unidade. Ao ativar alertas de conexão, os próximos controles são os limites dos alertas. As caixas de seleção também incluem dicas acessíveis explicando o que cada opção altera.

## Changelog

### 2.0

* Adicionado teste avançado com escolha manual de servidor e servidor favorito opcional, ativado por padrão.
* Adicionado resumo do histórico, filtros e exportação para CSV/JSON, ativado por padrão.
* Adicionados alertas configuráveis opcionais de conexão.
* Adicionado diagnóstico simples opcional após cada teste.
* Adicionadas unidades de exibição configuráveis opcionais.
* Diagnóstico, unidades personalizadas e alertas ficam desativados por padrão e podem ser ativados em Configurações.
* Controles da janela principal reorganizados para separar ações do histórico e configurações, melhorando a navegação pelo teclado.
* Atualizada a compatibilidade declarada até o NVDA `2026.3`.
* Código reorganizado em módulos menores para facilitar manutenção.

### 1.1

* Quando não há itens no histórico, agora é informado "Nenhum teste encontrado" em vez de "lista desconhecida".
* Agora é possível copiar itens dos detalhes para a área de transferência usando `Ctrl+C` ou o botão **Copiar item selecionado**.

### 1.0

* Primeira versão do complemento.

## Perguntas frequentes

* **Preciso de internet para usar?**
  Sim.

* **O que significa ping?**
  É o tempo de resposta entre seu computador e o servidor de teste.

* **Posso escolher o servidor?**
  Sim. Use **Teste avançado...**.

* **O que acontece ao lembrar um servidor?**
  Ele fica pré-selecionado na próxima vez que você abrir a tela de teste avançado. O teste rápido continua usando seleção automática.

* **Onde encontro o histórico?**
  O histórico aparece na janela principal do NVDA SpeedTest.

* **Como mudo o atalho?**
  Em **Preferências > Definir comandos**, procure por **NVDA SpeedTest**.

## Suporte e comunidade

Repositório oficial:
[https://github.com/leoguimaoficial/NVDA-SpeedTest](https://github.com/leoguimaoficial/NVDA-SpeedTest)

Add-on criado por Leo Guima.
