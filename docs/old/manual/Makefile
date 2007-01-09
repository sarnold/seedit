INSTALLDIR=doc

install: manual.pdf html
	mkdir -p $(INSTALLDIR)
	mv manual.pdf $(INSTALLDIR)/simplified_policy_manual.pdf
	mv manual $(INSTALLDIR)/simplified_policy_manual
html: manual.dvi
	latex2html  -show_section_numbers -link 2 -split +2 manual.tex

manual.pdf: manual.dvi 
	dvipdf manual.dvi

manual.dvi: *.tex
	latex manual.tex
	latex manual.tex
	latex manual.tex

view:	manual.pdf
	xpdf manual.pdf

clean:
	rm manual.pdf manual.dvi manual.aux manual.toc

