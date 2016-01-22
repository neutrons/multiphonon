
#!/usr/bin/perl -w

printf("Content-Type: image/png\n");
printf("Cache-Control: no-cache\n");
#printf("Set-Cookie: nop=".$$."\n");
printf("Expires: Thu, 22 Mar 2007 01:00:00 GMT\n");
printf("\n");

my $n="../a.png";
$$%2==0 && ($n="../b.png");

use IO::File;
my $io=new IO::File("<".$n);
my $buf="";
while(my $nr=$io->sysread($buf,65536)) {
  printf("%s",$buf);
}
