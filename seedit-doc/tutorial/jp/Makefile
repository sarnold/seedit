INSTALLDIR=doc

all: html tutorial.pdf

install: tutorial.pdf html
	mkdir -p $(INSTALLDIR)
	mv tutorial.pdf $(INSTALLDIR)/tutorial.pdf
	mv tutorial $(INSTALLDIR)/tutorial
html: tutorial.dvi
	latex2html  -show_section_numbers -link 2 -split +0 tutorial.tex
	mv tutorial tutorial_jp

tutorial.pdf: tutorial.dvi 
	pdvips tutorial.dvi
	ps2pdf13 tutorial.ps

tutorial.dvi: *.tex
	platex tutorial.tex
	platex tutorial.tex
	platex tutorial.tex

dvi: tutorial.dvi
	pxdvi tutorial.dvi
view:	tutorial.pdf
	xpdf tutorial.pdf

clean:
	rm *.pdf *.dvi *.aux *.toc

