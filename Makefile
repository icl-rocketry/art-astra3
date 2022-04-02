SRC_PATH = ./separation/sw/src

files = $(wildcard $(SRC_PATH)/*.py)

copy: $(files)
	@echo $? | xargs -n 1 echo | xargs -I{} cp ./{} /mnt/astra3
	@touch $@

clean: FORCE
	rm copy

mount: FORCE
	sudo mount /dev/sda1 /mnt/astra3

monitor: FORCE
	minicom -b 115200 -o -D /dev/ttyACM0

umount: FORCE
	sudo umount /mnt/astra3

FORCE: ;