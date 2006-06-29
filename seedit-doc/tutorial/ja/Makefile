prefix=/usr
INSTALLDIR = $(prefix)/share/doc/seedit/manual/ja

all: html

install: html
	mkdir -p $(INSTALLDIR)
	install -m 644  tutorial_jp/* $(INSTALLDIR)

html: dvi
	rm -rf tutorial_jp
	rm -rf install_jp
	latex2html  -show_section_numbers -link 2 -split +1 tutorial.tex
	latex2html  -show_section_numbers -link 2 -split +0 install.tex
	mv tutorial tutorial_jp
	mv install install_jp

pdf: dvi
	dvipdfmx tutorial.dvi 
	dvipdfmx install.dvi 
	mv tutorial.pdf tutorial_jp.pdf
	mv install.pdf install_jp.pdf

bb:
	ebb images/*.png
	mv *.bb images

dvi: *.tex bb
	platex tutorial.tex
	platex tutorial.tex
	platex tutorial.tex
	platex install.tex
	platex install.tex
	platex install.tex

view:	pdf
	acroread tutorial_jp.pdf
	acroread install_jp.pdf

clean:
	rm -rf *.pdf *.dvi *.aux *.toc 
	rm -rf tutorial_jp install_jp tutorial install



