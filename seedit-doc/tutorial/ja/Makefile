INSTALLDIR=doc

all: html pdf


install: pdf html
	mkdir -p $(INSTALLDIR)
	mv tutorial.pdf $(INSTALLDIR)/tutorial.pdf
	mv tutorial $(INSTALLDIR)/tutorial
html: dvi
	latex2html  -show_section_numbers -link 2 -split +0 tutorial.tex
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
	latex tutorial.tex
	latex tutorial.tex
	latex tutorial.tex
	latex install.tex
	latex install.tex
	latex install.tex

view:	pdf
	xpdf tutorial_jp.pdf
	xpdf install_jp.pdf

clean:
	rm *.pdf *.dvi *.aux *.toc 
	rm -rf tutorial_jp install_jp



