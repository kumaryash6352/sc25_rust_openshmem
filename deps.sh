
set -euxo pipefail

HERE=$(pwd)
mkdir -p build
mkdir -p install
mkdir -p install/bin

export PATH=$HERE/install/bin:$PATH

# grab things we need

# python venv
if [ ! -d "$HERE/install/bin/activate" ]; then
	python3 -m venv "$HERE/install"
fi
source "$HERE/install/bin/activate"

# ofi
if [ ! -f "$HERE/install/lib/libfabric.so" ]; then
	pushd "$HERE/build/"
	if [ ! -d "$HERE/build/libfabric" ]; then
		git clone --recursive https://github.com/ofiwg/libfabric.git libfabric
		cd libfabric
		git checkout cf173800a23505a0c6ec9ad42b935bde60a57da2
	fi
	cd "$HERE/build/libfabric"
	./autogen.sh
	./configure --prefix="$HERE/install" \
		    --enable-tcp=yes
	make -j
	make install
	popd
fi

# sos
if [ ! -f "$HERE/install/lib/libsma.so" ]; then
	pushd "$HERE/build/"
	if [ ! -d "$HERE/build/sos" ]; then
		git clone --recursive https://github.com/Sandia-OpenSHMEM/SOS.git sos
		cd sos
		git checkout 45e6e7eb1a9b099a418237a9e677eb6603222c84
	fi
	cd "$HERE/build/sos"
	./autogen.sh
	./configure --prefix="$HERE/install" \
		    --with-ofi="$HERE/install" \
		    --disable-fortran \
		    --enable-pmi-simple
	make -j
	make install
	popd
fi
export SHMEM_INSTALL_DIR="$HERE/install"


# shmem4py
if ! python -c "import shmem4py" ; then
	pushd "$HERE/build/"
	git clone https://github.com/mpi4py/shmem4py shmem4py
	cd shmem4py
	git checkout 0a3b0a019699ac8e46c54db9d0d2bf1941693e45
	pip3 install .
	popd
fi

# rustup
if [ ! -x rustc ]; then
	pushd "$HERE/install/"
	export RUSTUP_HOME="$HERE/install"
	export CARGO_HOME="$HERE/install"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
		| sh -s -- --default-toolchain none -y --no-modify-path
	popd
fi

# finally, shmembench
if [ ! -d "$HERE/shmembench" ]; then
	git clone https://github.com/michael-beebe/shmembench.git shmembench
	cd shmembench
	git checkout edc0e30fd2eb8b86a0708325d0b4175408afd862
fi
if [ ! -f "$HERE/install/bin/shmembench" ]; then
	pushd "$HERE/shmembench"
	CC="$HERE/install/bin/oshcc" make -j
	cp shmembench "$HERE/install/bin/shmembench"
fi
if [ ! -f "$HERE/install/bin/shmembench-rs" ]; then
	pushd "$HERE/shmembench/rs"
	rustup run --install nightly-2025-04-09 cargo build --release
	cp ./target/release/shmembench-rs "$HERE/install/bin/shmembench-rs"
fi

