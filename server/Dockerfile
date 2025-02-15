FROM alpine

RUN apk add --no-cache py3-pip

WORKDIR /app

RUN python3 -m pip install --no-cache-dir --break-system-packages waitress

COPY req.txt .
RUN python3 -m pip install --no-cache-dir --break-system-packages -r req.txt

COPY ./ .

EXPOSE 5000/tcp

ENTRYPOINT ["waitress-serve"] 
CMD ["--host", "0.0.0.0", "--port", "5000", "--call", "app:createApp"]