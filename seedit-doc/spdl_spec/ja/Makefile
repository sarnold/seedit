prefix=/usr
INSTALLDIR = $(prefix)/share/doc/seedit/spdl_spec/ja

all: html

install: html
	mkdir -p $(INSTALLDIR)
	install -m 644 $(INSTALLDIR)

html: dvi
	rm -rf spdl_spec_jp
	latex2html  -local_icons -show_section_numbers -link 2 -split +1 spdl_spec.tex
	mv spdl_spec spdl_spec_jp

pdf: dvi
	dvipdfmx spdl_spec.dvi 
	mv spdl_spec.pdf spdl_spec_jp.pdf


dvi: *.tex 
	platex spdl_spec.tex
	platex spdl_spec.tex
	platex spdl_spec.tex

view:	pdf
	acroread spdl_spec.pdf

clean:
	rm -rf *.pdf *.dvi *.aux *.toc 
	rm -rf spdl_spec_jp  install



