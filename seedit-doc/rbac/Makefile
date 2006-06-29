prefix=/usr
INSTALLDIR = $(prefix)/share/doc/seedit

all:html 

install:  html
	mkdir -p $(INSTALLDIR)
	mv rbac_guide $(INSTALLDIR)

html: rbac_guide.dvi
	latex2html  -show_section_numbers -link 2 -split +2 rbac_guide.tex

rbac_guide.pdf: rbac_guide.dvi 
	dvipdf rbac_guide.dvi

rbac_guide.dvi: *.tex
	latex rbac_guide.tex
	latex rbac_guide.tex
	latex rbac_guide.tex


view:	rbac_guidepdf
	xpdf rbac_guide.pdf

clean:
	rm -rf *.pdf *.dvi *.aux *.toc rbac_guide *.log

