#!/bin/bash

echo "local host is $(hostname)" 

module load tools/redis-4.0.8
redis-server --protected-mode no  & 

