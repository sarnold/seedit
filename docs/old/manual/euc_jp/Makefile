INSTALLDIR=doc

install: html manual.pdf
	mkdir -p $(INSTALLDIR)
	mv manual.pdf $(INSTALLDIR)/simplified_policy_manual_ja.pdf
	mv manual $(INSTALLDIR)/simplified_policy_manual_ja
html:
	latex2html  -show_section_numbers -link 2 -split +2 manual.tex

manual.pdf: manual.dvi 
	pdvips manual.dvi
	ps2pdf14 manual.ps

manual.dvi: *.tex
	platex manual.tex
	platex manual.tex
	platex manual.tex

view:	manual.pdf
	xpdf manual.pdf


