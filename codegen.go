package main

type CodeGen interface {
	setName(string)
	addPort(string)
	toString() string
}
