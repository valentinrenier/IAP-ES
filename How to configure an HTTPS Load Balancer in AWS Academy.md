# How to configure an HTTPS Load Balancer in AWS Academy



This guide showcases how you can configure HTTPS on an AWS Load Balancer. To avoid that students have to deal with DNS aspects, this guide involves updating /etc/hosts to map the certificate’s domain to the Load Balancer’s IPs. Thus, HTTPS protected communication with the Load Balancer will only be possible if /etc/hosts is updated.

## Initial Scenario

- A Load Balancer deployed on AWS
- The Load Balancer is configured with an HTTP Only listener (port 80)

![https://i.imgur.com/N8vBjaG.png](https://i.imgur.com/N8vBjaG.png)

## From an HTTP Listener to an HTTPS Listener

You should edit the Listener:

- **Protocol:** HTTPS
- **Port:** 443
- **Security Policy Name:** ELBSecurityPolicy-TLS13-1-2-2021-06 (recommended)
- **Certificate Source:** Import Certificate
- **Certificate Import Destination:** Import to ACM - recommended

In `Certificate Private Key`, input the following:

```
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgZ2fZMq5mTZp+OeIW
hxox8qLxnb+aQxn0po9NPx/0hHShRANCAASleHjAlq3+1vfjKPITLu3Q6ZaU9owj
xT59qVV5kYG606l/AKqeRq0OQr8h1Nhdq4sI2bspx0+aql9bM0452pb5
-----END PRIVATE KEY-----
```

In `Certificate Body`, paste the following:

```
-----BEGIN CERTIFICATE-----
MIIDfDCCAwGgAwIBAgISBKoayTFy9ZV7N1mnva6Mu/KBMAoGCCqGSM49BAMDMDIx
CzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQDEwJF
NjAeFw0yNDEwMjAwODA1MTZaFw0yNTAxMTgwODA1MTVaMBkxFzAVBgNVBAMTDmVz
LXVhLmRkbnMubmV0MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEpXh4wJat/tb3
4yjyEy7t0OmWlPaMI8U+falVeZGButOpfwCqnkatDkK/IdTYXauLCNm7KcdPmqpf
WzNOOdqW+aOCAg4wggIKMA4GA1UdDwEB/wQEAwIHgDAdBgNVHSUEFjAUBggrBgEF
BQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAdBgNVHQ4EFgQUUWKIiRnhrv0R
hgwT1/383Xwou0kwHwYDVR0jBBgwFoAUkydGmAOpUWiOmNbEQkjbI79YlNIwVQYI
KwYBBQUHAQEESTBHMCEGCCsGAQUFBzABhhVodHRwOi8vZTYuby5sZW5jci5vcmcw
IgYIKwYBBQUHMAKGFmh0dHA6Ly9lNi5pLmxlbmNyLm9yZy8wGQYDVR0RBBIwEIIO
ZXMtdWEuZGRucy5uZXQwEwYDVR0gBAwwCjAIBgZngQwBAgEwggECBgorBgEEAdZ5
AgQCBIHzBIHwAO4AdQDm0jFjQHeMwRBBBtdxuc7B0kD2loSG+7qHMh39HjeOUAAA
AZKpKxjEAAAEAwBGMEQCIC3JRDouyBmbe0k1Md4D31QYDQ996khecbe1ZYTK9oTG
AiAkThF9EH4/BXIhzyRAFTKPSN81/xJ/jhb7H7Zf/KezxwB1AM8RVu7VLnyv84db
2Wkum+kacWdKsBfsrAHSW3fOzDsIAAABkqkrGOIAAAQDAEYwRAIgCmS8BzMA+mke
RPHwENSnWMUadn4tiVmBWHZN651bbPQCIGNps78nbyEXUvKvAluKH5A8K33ujU04
O/p3yQAStp3wMAoGCCqGSM49BAMDA2kAMGYCMQCJlJK+pwcKI/zRkLh1946G9/xX
ctFYFKxVliaEnKZIFX8SkdCNPbj4aQ6cNxRb+ukCMQC+iQXYLzu+yQj5/1trCfYd
faxLzbXT+QwAzPcluWa74i0mKGUaxmUnSThT3jVVzH8=
-----END CERTIFICATE-----
```

You can leave `Certificate Chain - optional` empty

After this, the Listener will be updated with the certificate. See the following image.

![https://i.imgur.com/eZ0UdER.png](https://i.imgur.com/eZ0UdER.png)

As you can see, the certificate that you uploaded corresponds to the domain: `es-ua.ddns.net`

## Test the HTTPS Listener

After updating the listener, to access the Load Balancer using HTTPS. In your browser access 

`https://<LB_DOMAIN>`  (example: `https://web-alb-1005027590.us-east-1.elb.amazonaws.com`)

You should be presented with the following error.

![https://i.imgur.com/T84OAp9.png](https://i.imgur.com/T84OAp9.png)

Please notice that the error is the following: `net::ERR_CERT_COMMON_NAME_INVALID`

This error was expected, as the HTTPS Listener is using certificates created for the domain `es-ua.ddns.net` but we are accessing it via the LB’s domain. Since the domains don’t match, we get this error.

The next step is for you to fool your machine “to think” that the  [`es-ua.ddns.net`](http://es-ua.ddns.net) is the domain of the Load Balancer. For that you will have to update `/etc/hosts` and map the domain `es-ua.ddns.net` to the public IPs of the Load Balancer

## Update /etc/hosts

The firsts step is to know which IPs were assigned to the Load Balancer. For that, you may execute the following command:

```bash
host <LB_DOMAIN> 

# Example
# → host web-alb-1005027590.us-east-1.elb.amazonaws.com
# web-alb-1005027590.us-east-1.elb.amazonaws.com has address 52.55.44.55
# web-alb-1005027590.us-east-1.elb.amazonaws.com has address 54.157.215.73
```

As you can see, the Load Balancer has two IPv4 Addresses:

- 52.55.44.55
- 54.157.215.73

Now we need to add the following lines to `/etc/hosts`: 

```
52.55.44.55     es-ua.ddns.net
54.157.215.73   es-ua.ddns.net
```

After this, you may try to access the Load Balancer via the domain of the certificate, that we have now added on `/etc/hosts`. In your browser, access `https://es-ua.ddns.net`

![https://i.imgur.com/e4hQYSZ.png](https://i.imgur.com/e4hQYSZ.png)

Now you can access your HTTPS LB, via a custom domain 🙂

## Questions

If you have any questions, contact prof. Rafael Direito (rafael.neves.direito@ua.pt)