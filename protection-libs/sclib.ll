; ModuleID = 'sclib.bc'
source_filename = "rtlib.c"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: alwaysinline nounwind uwtable
define dso_local void @guardMe(i32) #0 {
  %2 = alloca i32, align 4
  %3 = alloca i8*, align 8
  %4 = alloca i8, align 1
  %5 = alloca i8, align 1
  %6 = alloca i32, align 4
  %7 = alloca i8, align 1
  store i32 %0, i32* %2, align 4
  %8 = load i32, i32* %2, align 4
  %9 = zext i32 %8 to i64
  %10 = inttoptr i64 %9 to i8*
  store i8* %10, i8** %3, align 8
  %11 = load i32, i32* %2, align 4
  %12 = trunc i32 %11 to i8
  store i8 %12, i8* %4, align 1
  %13 = load i32, i32* %2, align 4
  %14 = trunc i32 %13 to i8
  store i8 %14, i8* %5, align 1
  store i32 0, i32* %6, align 4
  store i8 0, i8* %7, align 1
  br label %15

; <label>:15:                                     ; preds = %20, %1
  %16 = load i32, i32* %6, align 4
  %17 = load i8, i8* %4, align 1
  %18 = zext i8 %17 to i32
  %19 = icmp ult i32 %16, %18
  br i1 %19, label %20, label %31

; <label>:20:                                     ; preds = %15
  %21 = load i8*, i8** %3, align 8
  %22 = getelementptr inbounds i8, i8* %21, i32 1
  store i8* %22, i8** %3, align 8
  %23 = load i8, i8* %21, align 1
  %24 = zext i8 %23 to i32
  %25 = load i8, i8* %7, align 1
  %26 = zext i8 %25 to i32
  %27 = xor i32 %26, %24
  %28 = trunc i32 %27 to i8
  store i8 %28, i8* %7, align 1
  %29 = load i32, i32* %6, align 4
  %30 = add i32 %29, 1
  store i32 %30, i32* %6, align 4
  br label %15

; <label>:31:                                     ; preds = %15
  %32 = load i8, i8* %7, align 1
  %33 = zext i8 %32 to i32
  %34 = load i8, i8* %5, align 1
  %35 = zext i8 %34 to i32
  %36 = icmp ne i32 %33, %35
  br i1 %36, label %37, label %38

; <label>:37:                                     ; preds = %31
  call void @exit(i32 1) #2
  unreachable

; <label>:38:                                     ; preds = %31
  ret void
}

; Function Attrs: noreturn nounwind
declare dso_local void @exit(i32) #1

attributes #0 = { alwaysinline nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { noreturn nounwind "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { noreturn nounwind }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"clang version 7.0.0-3 (tags/RELEASE_700/final)"}
