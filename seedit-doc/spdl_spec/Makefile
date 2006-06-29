prefix=/usr
INSTALLDIR = $(prefix)/share/doc/seedit

all:html 

install:  html
	mkdir -p $(INSTALLDIR)
	mv spel_spec $(INSTALLDIR)

html: spdl_spec.dvi
	latex2html  -show_section_numbers -link 2 -split +2 spdl_spec.tex

spdl_spec.pdf: spdl_spec.dvi 
	dvipdf spdl_spec.dvi

spdl_spec.dvi: *.tex
	latex spdl_spec.tex
	latex spdl_spec.tex
	latex spdl_spec.tex

view:	spdl_spec.pdf
	xpdf spdl_spec.pdf

clean:
	rm -rf *.pdf *.dvi *.aux *.toc spdl_spec *.log

