INSTALLDIR=doc

all: html tutorial.pdf

install: tutorial.pdf html
	mkdir -p $(INSTALLDIR)
	mv tutorial.pdf $(INSTALLDIR)/tutorial.pdf
	mv tutorial $(INSTALLDIR)/tutorial
html: tutorial.dvi
	latex2html  -show_section_numbers -link 2 -split +0 tutorial.tex

tutorial.pdf: tutorial.dvi 
	dvipdf tutorial.dvi

tutorial.dvi: *.tex
	latex tutorial.tex
	latex tutorial.tex
	latex tutorial.tex

view:	tutorial.pdf
	xpdf tutorial.pdf

clean:
	rm *.pdf *.dvi *.aux *.toc

