all: html access_vectors.pdf
html: access_vectors.dvi
	latex2html -local_icons -show_section_numbers -link 2 -split 0 access_vectors.tex

access_vectors.pdf: access_vectors.dvi
	dvipdf access_vectors.dvi

access_vectors.dvi: *.tex
	latex access_vectors.tex
	latex access_vectors.tex
	latex access_vectors.tex

view:   access_vectors.pdf
	xpdf access_vectors.pdf

clean: 
	rm -rf access_vectors.dvi access_vectors.pdf access_vectors

