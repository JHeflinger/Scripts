# create build directory if it does not exist
if [ ! -d "build" ]; then
	mkdir "build"
fi

# download builder
if [ ! -f "build/tiny_linux.bin" ] || [ "$1" == "-u" ] || [ "$2" == "-u" ]; then
	if [ -f "build/tiny_linux.bin" ]; then
		echo "Updating tiny builder..."
		rm build/tiny_linux.bin
	else
		echo "Downloading tiny builder..."
	fi
	cd build
	wget -q https://github.com/JHeflinger/tiny/raw/refs/heads/main/bin/tiny_linux.bin
	chmod +x tiny_linux.bin
	cd ..
fi

# run builder
PROD=""
if [ "$1" == "-p" ] || [ "$2" == "-p" ]; then
	PROD="-prod"
fi
./build/tiny_linux.bin -a $PROD
if [ $? -ne 0 ]; then
	exit 1
fi
