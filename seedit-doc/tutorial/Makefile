prefix=/usr
INSTALLDIR = $(prefix)/share/doc/seedit

all: html 

install: all
	mkdir -p $(INSTALLDIR)
	mv tutorial $(INSTALLDIR)/manual/en

html: dvi
	latex2html  -show_section_numbers -link 2 -split +1 tutorial.tex
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

