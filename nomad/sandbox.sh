#!/usr/bin/env bash


function start-consul() {
    consul agent --dev --bind 0.0.0.0 --client 0.0.0.0
}


function start-nomad() {
    nomad agent -dev-connect --bind 0.0.0.0
}

start-consul & 
start-nomad &
