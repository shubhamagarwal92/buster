# Example usage

1. Create `examples.json` in the [resources](./resources/) which are shown on the gradio app. Sample examples [here](./resources/examples.sample.json)
2. Create `auth.json` in the [resources](./resources/) which are used as credentials. Sample json [here](./resources/auth.sample.json)

We can use this code when we already have the docs build locally. Then just point to the directory in [create_chunks.py](./create_chunks.py)

We also allow scraping of the website using `httrack`.

## Installation

Install all the packages as defined [here](../../README.md). 

For installing httrack: 

#### On Mac
```
brew install httrack
```

#### On Linux

```
sudo apt-get install httrack
```

If you dont have sudo rights, you can follow ChatGPT (https://chat.openai.com/share/92435ebd-1d2f-4c7a-8bfb-d140449ba457) or do

```
git clone https://github.com/xroche/httrack.git --recurse
cd httrack

./configure --prefix="$HOME/httrack_install"
make -j8
make install
```

If it fails, try installing zlib as 
```
wget https://zlib.net/zlib.tar.gz
tar -xzf zlib.tar.gz
cd zlib-1.2.13
# ./configure --prefix="/mnt/home/packages/zlib_install"

./configure --prefix="$HOME/zlib_install"
make
make install
```

You might also have to install openssl as: 
```
wget https://www.openssl.org/source/openssl-1.1.1l.tar.gz
tar -xzf openssl-1.1.1l.tar.gz
cd openssl-1.1.1l
./config --prefix="$HOME/openssl_install"
# ./config --prefix="/mnt/home/packages/openssl_install"
make
make install

export LD_LIBRARY_PATH="/mnt/home/packages/openssl_install/lib:$LD_LIBRARY_PATH"
```

Now install httrack with the flags
```
cd path/to/httrack
./configure --prefix="$HOME/httrack_install" --with-zlib="$HOME/zlib_install" --with-openssl="$HOME/openssl_install"
# ./configure --prefix="/mnt/home/packages/httrack_install" --with-zlib="/mnt/home/packages/zlib_install" CPPFLAGS="-I/mnt/home/packages//openssl_install/include" LDFLAGS="-L/mnt/home/packages/openssl_install/lib"

make -j8
make install
```

Also export these paths to `.bashrc` as 
```
vi ~/.bashrc

export LD_LIBRARY_PATH="/mnt/home/packages/openssl_install/lib:$LD_LIBRARY_PATH"
export PATH="/mnt/home/packages/httrack_install//bin:$PATH"
```

Now use as

```
httrack 'https://docs.mila.quebec/' -O resources/mila_docs_root_dir
```


## Running

We have provided a bash script to run the whole pipeline as

```
bash pipeline.sh
```
Follow the instructions on the terminal. 

This would ideally call

1. `httrack "$BASE_URL" -O "${RESOURCES_DIR}"/docs_root_dir`
2. python create_chunks.py
3. python generate_embeddings.py
4. python gradio_app.py
