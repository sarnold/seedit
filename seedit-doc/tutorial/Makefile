INSTALLDIR=doc

all: html pdf

install: tutorial.pdf html
	mkdir -p $(INSTALLDIR)
	mv tutorial.pdf $(INSTALLDIR)/tutorial.pdf
	mv tutorial $(INSTALLDIR)/tutorial
html: dvi
	latex2html  -show_section_numbers -link 2 -split +0 tutorial.tex
	latex2html  -show_section_numbers -link 2 -split +0 install.tex

pdf:  dvi
	dvipdfm tutorial.dvi 
	dvipdfm install.dvi 

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
	xpdf tutorial.pdf
	xpdf install.pdf

clean:
	rm *.pdf *.dvi *.aux *.toc
	rm -rf tutorial install

