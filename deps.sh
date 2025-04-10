
set -euxo pipefail

HERE=$(pwd)
mkdir -p build
mkdir -p install
mkdir -p install/bin
mkdir -p metadata

export PATH=$HERE/install/bin:$PATH
export CC=${CC:-cc}

# dump env to metadata
env > "$HERE/metadata/preenv"
$CC --version > "$HERE/metadata/cc"
$CC --version --verbose > "$HERE/metadata/ccv"

# grab things we need

# python venv
if [ ! -d "$HERE/install/bin/activate" ]; then
	python3 -m venv "$HERE/install"
fi
source "$HERE/install/bin/activate"
python3 --version > "$HERE/metadata/py"

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
python3 -m pip freeze > "$HERE/metadata/pipfreeze"

# rustup
if [ ! -x rustc ]; then
	pushd "$HERE/install/"
	export RUSTUP_HOME="$HERE/install"
	export CARGO_HOME="$HERE/install"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
		| sh -s -- --default-toolchain none -y --no-modify-path
	popd
fi

# shmembench
if [ ! -d "$HERE/build/shmembench" ]; then
	pushd "$HERE/build"
	git clone https://github.com/michael-beebe/shmembench.git shmembench
	cd shmembench
	git checkout edc0e30fd2eb8b86a0708325d0b4175408afd862
	popd
fi
if [ ! -f "$HERE/install/bin/shmembench" ]; then
	pushd "$HERE/build/shmembench"
	CC="$HERE/install/bin/oshcc" make -j
	cp shmembench "$HERE/install/bin/shmembench"
	popd
fi
if [ ! -f "$HERE/install/bin/shmembench-rs" ]; then
	pushd "$HERE/build/shmembench/rs"
	rustup run --install nightly-2025-04-09 cargo build --release
	cp ./target/release/shmembench-rs "$HERE/install/bin/shmembench-rs"
	popd
fi
if [ ! -f "$HERE/install/bin/shmembench4py.py" ]; then
	cp "$HERE/build/shmembench/py/main.py" "$HERE/install/bin/shmembench4py.py"
fi
if [ ! -f "$HERE/install/bin/compare.py" ]; then
	cp "$HERE/build/shmembench/compare.py" "$HERE/install/bin/compare.py"
fi

# lastly, we need openshmem_rs separately
# because in my infinite wisdom, the bfs
# is part of the repo but shmembench-rs isn't
if [ ! -f "$HERE/build/openshmem_rs" ]; then
	git clone https://github.com/kumaryash6352/openshmem_rs.git openshmem_rs
	pushd "$HERE/build/openshmem_rs"
	git checkout 9d2bdf3799148236b3d382b5aafdc609a5dff8c2
	popd
fi
if [ ! -f "$HERE/install/bin/bfs-graph-search" ]; then
	pushd "$HERE/build"
	cd openshmem_rs/bench/graphsearch
	rustup run --install nightly-2025-04-09 cargo build --release
	cp "$HERE/build/openshmem_rs/target/release/bfs-graph-search" "$HERE/install/bin/bfs-graph-search"
	popd
fi
if [! -f "$HERE/metadata/searchlist" ] || [ ! -f "$HERE/metadata/edgelist" ]; then
	pushd "$HERE/build/openshmem_rs/bench/graphsearch"
	"$HERE/install/bin/python3" make_edgelist.py
fi

# and a script to activate the "environment"
if [ ! -f "$HERE/activate" ]; then
	cat > "$HERE/activate" << EOF
export PATH="$HERE/install/bin:\$PATH"
export LD_LIBRARY_PATH="$HERE/install/lib:\$LD_LIBRARY_PATH"
export LIBRARY_PATH="$HERE/install/lib:\$LIBRARY_PATH"
export C_INCLUDE_PATH="$HERE/install/include:\$C_INCLUDE_PATH"
export CPLUS_INCLUDE_PATH="$HERE/install/include:\$CPLUS_INCLUDE_PATH"
export CXX_INCLUDE_PATH="$HERE/install/include:\$CPLUS_INCLUDE_PATH"
EOF
fi
