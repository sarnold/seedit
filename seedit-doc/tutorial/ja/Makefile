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
	dvipdfmx tutorial.dvi
	mv tutorial.pdf tutorial_jp.pdf

bb:
	ebb images/*.png
	mv *.bb images

tutorial.dvi: *.tex bb
	platex tutorial.tex
	platex tutorial.tex
	platex tutorial.tex

pdf: tutorial.dvi
	pvipdfmx tutorial.dvi

view:	tutorial_jp.pdf
	xpdf tutorial_jp.pdf

clean:
	rm *.pdf *.dvi *.aux *.toc

