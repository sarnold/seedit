INSTALLDIR=doc

all: html tutorial_jp.pdf

install: tutorial_jp.pdf html
	mkdir -p $(INSTALLDIR)
	mv tutorial.pdf $(INSTALLDIR)/tutorial.pdf
	mv tutorial $(INSTALLDIR)/tutorial
html: tutorial.dvi
	latex2html  -show_section_numbers -link 2 -split +0 tutorial.tex
	rm -rf tutorial_jp
	mv tutorial tutorial_jp

tutorial_jp.pdf: tutorial.dvi 
	pdvips tutorial.dvi
	ps2pdf13 tutorial.ps
	mv tutorial.pdf tutorial_jp.pdf	
bb:
	ebb images/*.png
	mv *.bb images

tutorial.dvi: *.tex bb
	platex tutorial.tex
	platex tutorial.tex
	platex tutorial.tex

dvi: tutorial.dvi
	pxdvi tutorial.dvi
view:	tutorial.pdf
	xpdf tutorial.pdf

clean:
	rm *.pdf *.dvi *.aux *.toc

